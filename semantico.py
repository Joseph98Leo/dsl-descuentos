"""
Etapa 4 — Análisis semántico y generación del objeto JSON.

Recibe el AST que produce sintactico.py y comprueba lo que la gramática no
puede expresar:

  Validaciones de cada regla (errores)
    - El atributo existe para el objeto (tabla de símbolos dominio.json).
    - El valor es del tipo correcto: número para atributos numéricos y un valor
      permitido para atributos categóricos (que solo admiten = / == / !=).
    - El periodo de TIEMPO(…) existe.
    - El porcentaje de descuento está entre 0% y 100%.
    - La condición de cada rama puede cumplirse (no es una contradicción,
      por ejemplo COMPRA.total > 500 Y COMPRA.total < 100).

  Ambigüedades (advertencias)
    - Rama SINO SI / SINO inalcanzable: las ramas anteriores ya cubren todos
      sus casos, así que nunca se aplicará.

  Colisiones entre reglas (OE3)
    - Dos reglas distintas que pueden aplicarse en la misma transacción y
      acumular descuentos. Se demuestra con un ejemplo concreto de compra.

La detección es exacta: cada condición se pasa a forma normal disyuntiva y se
comprueba si la conjunción de restricciones es satisfacible sobre el dominio
de cada atributo (intervalos para los numéricos, conjuntos para los categóricos).
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

DOMINIO = json.loads((Path(__file__).resolve().parent / "dominio.json").read_text(encoding="utf-8"))

NEGACION = {"==": "!=", "!=": "==", ">": "<=", "<=": ">", "<": ">=", ">=": "<"}
MAX_CONJUNCIONES = 256


class CondicionCompleja(Exception):
    pass


# =============================================================================
# 1. Validación de cada comparación (tabla de símbolos y tipos)
# =============================================================================

def _error(codigo, regla, nodo, mensaje):
    return {"codigo": codigo, "regla": regla, "linea": nodo.get("linea"), "columna": nodo.get("columna"),
            "mensaje": f"Línea {nodo.get('linea')}, columna {nodo.get('columna')}: {mensaje}"}


def _validar_condicion(nodo, regla, errores):
    tipo = nodo["tipo"]
    if tipo in ("Y", "O"):
        for h in nodo["operandos"]:
            _validar_condicion(h, regla, errores)
    elif tipo == "NO":
        _validar_condicion(nodo["operando"], regla, errores)
    elif tipo == "tiempo":
        if nodo["periodo"] not in DOMINIO["periodos"]:
            validos = ", ".join(DOMINIO["periodos"])
            errores.append(_error("PERIODO_DESCONOCIDO", regla, nodo,
                                  f"el periodo «{nodo['periodo']}» no existe. Periodos válidos: {validos}."))
    elif tipo == "comparacion":
        _validar_comparacion(nodo, regla, errores)


def _validar_comparacion(c, regla, errores):
    objeto, atributo, op = c["objeto"], c["atributo"], c["operador"]
    valor, token = c["valor"]["texto"], c["valor"]["token"]
    atributos = DOMINIO["objetos"][objeto]
    if atributo not in atributos:
        errores.append(_error("ATRIBUTO_DESCONOCIDO", regla, c,
                              f"{objeto} no tiene el atributo «{atributo}». Atributos válidos: {', '.join(atributos)}."))
        return
    info = atributos[atributo]
    nombre = f"{objeto}.{atributo}"
    if info["tipo"] == "numerico":
        if token != "T_NUM":
            errores.append(_error("TIPO_INCOMPATIBLE", regla, c["valor"],
                                  f"{nombre} es numérico y se compara con «{valor}»; se esperaba un número."))
    else:
        if token != "T_ID":
            errores.append(_error("TIPO_INCOMPATIBLE", regla, c["valor"],
                                  f"{nombre} es categórico y se compara con «{valor}»; se esperaba uno de: "
                                  f"{', '.join(info['valores'])}."))
        elif valor not in info["valores"]:
            errores.append(_error("VALOR_NO_PERMITIDO", regla, c["valor"],
                                  f"«{valor}» no es un valor válido de {nombre}. Valores válidos: "
                                  f"{', '.join(info['valores'])}."))
        if op not in ("=", "==", "!="):
            errores.append(_error("OPERADOR_INVALIDO", regla, c,
                                  f"{nombre} es categórico: solo admite =, == o !=, no «{op}»."))


# =============================================================================
# 2. Forma normal negada y forma normal disyuntiva
# =============================================================================
# Literales:  ("cmp", "OBJETO.atributo", operador, valor)   ·   ("tiempo", periodo, positivo)

def _literal(c, negado):
    op = "==" if c["operador"] == "=" else c["operador"]
    if negado:
        op = NEGACION[op]
    clave = f"{c['objeto']}.{c['atributo']}"
    info = DOMINIO["objetos"][c["objeto"]][c["atributo"]]
    valor = Fraction(c["valor"]["texto"]) if info["tipo"] == "numerico" else c["valor"]["texto"]
    return ("cmp", clave, op, valor)


def fnn(nodo, negado=False):
    """Forma normal negada: empuja las negaciones (NO) hasta los literales."""
    tipo = nodo["tipo"]
    if tipo == "comparacion":
        return ("lit", _literal(nodo, negado))
    if tipo == "tiempo":
        return ("lit", ("tiempo", nodo["periodo"], not negado))
    if tipo == "NO":
        return fnn(nodo["operando"], not negado)
    hijos = [fnn(h, negado) for h in nodo["operandos"]]
    conector = tipo if not negado else ("O" if tipo == "Y" else "Y")
    return (conector, hijos)


def fnd(nodo):
    """Forma normal disyuntiva: lista de conjunciones (cada una, tupla de literales)."""
    if nodo[0] == "lit":
        return [(nodo[1],)]
    if nodo[0] == "O":
        resultado = []
        for h in nodo[1]:
            resultado.extend(fnd(h))
    else:  # "Y"
        resultado = [()]
        for h in nodo[1]:
            resultado = [a + b for a in resultado for b in fnd(h)]
            if len(resultado) > MAX_CONJUNCIONES:
                raise CondicionCompleja()
    if len(resultado) > MAX_CONJUNCIONES:
        raise CondicionCompleja()
    return resultado


def _y(*fnds):
    resultado = [()]
    for f in fnds:
        resultado = [a + b for a in resultado for b in f]
        if len(resultado) > MAX_CONJUNCIONES:
            raise CondicionCompleja()
    return resultado


def _no(nodo_fnn):
    """Negación de una condición ya en forma normal negada."""
    if nodo_fnn[0] == "lit":
        lit = nodo_fnn[1]
        if lit[0] == "cmp":
            return ("lit", ("cmp", lit[1], NEGACION[lit[2]], lit[3]))
        return ("lit", ("tiempo", lit[1], not lit[2]))
    conector = "O" if nodo_fnn[0] == "Y" else "Y"
    return (conector, [_no(h) for h in nodo_fnn[1]])


# =============================================================================
# 3. Satisfacibilidad de una conjunción (con ejemplo)
# =============================================================================

def _info(clave):
    objeto, atributo = clave.split(".", 1)
    return DOMINIO["objetos"][objeto][atributo]


def _numero(v: Fraction):
    return int(v) if v.denominator == 1 else round(float(v), 2)


def _valor_numerico(restricciones, info):
    lo = Fraction(info["min"]) if "min" in info else None
    hi = Fraction(info["max"]) if "max" in info else None
    lo_cerrado = hi_cerrado = True
    iguales, distintos = set(), set()
    for op, v in restricciones:
        if op == "==":
            iguales.add(v)
        elif op == "!=":
            distintos.add(v)
        elif op in (">", ">="):
            cerrado = op == ">="
            if lo is None or v > lo or (v == lo and not cerrado):
                lo, lo_cerrado = v, cerrado
        else:  # "<", "<="
            cerrado = op == "<="
            if hi is None or v < hi or (v == hi and not cerrado):
                hi, hi_cerrado = v, cerrado
    entero = info.get("entero", False)

    def dentro(x):
        if lo is not None and (x < lo or (x == lo and not lo_cerrado)):
            return False
        if hi is not None and (x > hi or (x == hi and not hi_cerrado)):
            return False
        return x not in distintos and (not entero or x.denominator == 1)

    if len(iguales) > 1:
        return None
    if iguales:
        v = next(iter(iguales))
        return v if dentro(v) else None

    intentos = len(distintos) + 2
    candidatos = []
    if entero:
        desde = None if lo is None else (math.ceil(lo) if lo_cerrado else math.floor(lo) + 1)
        hasta = None if hi is None else (math.floor(hi) if hi_cerrado else math.ceil(hi) - 1)
        if desde is not None:
            candidatos = [Fraction(desde + k) for k in range(intentos)]
        elif hasta is not None:
            candidatos = [Fraction(hasta - k) for k in range(intentos)]
        else:
            candidatos = [Fraction(k) for k in range(intentos)]
    else:
        if lo is not None and hi is not None:
            if lo > hi:
                return None
            candidatos = ([lo] if lo_cerrado else []) + [lo + (hi - lo) * k / (intentos + 1) for k in range(1, intentos + 1)]
            candidatos += [hi] if hi_cerrado else []
        elif lo is not None:
            candidatos = ([lo] if lo_cerrado else []) + [lo + k for k in range(1, intentos + 1)]
        elif hi is not None:
            candidatos = ([hi] if hi_cerrado else []) + [hi - k for k in range(1, intentos + 1)]
        else:
            candidatos = [Fraction(k) for k in range(intentos)]
    return next((c for c in candidatos if dentro(c)), None)


def satisfacible(conjuncion):
    """¿Existe una transacción que cumpla todos los literales? Devuelve el ejemplo o None."""
    por_clave, activos, inactivos = {}, set(), set()
    for lit in conjuncion:
        if lit[0] == "tiempo":
            (activos if lit[2] else inactivos).add(lit[1])
        else:
            por_clave.setdefault(lit[1], []).append((lit[2], lit[3]))
    if activos & inactivos:
        return None

    ejemplo = {}
    for clave, restricciones in por_clave.items():
        info = _info(clave)
        if info["tipo"] == "numerico":
            v = _valor_numerico(restricciones, info)
            if v is None:
                return None
            ejemplo[clave] = _numero(v)
        else:
            iguales = {v for op, v in restricciones if op == "=="}
            distintos = {v for op, v in restricciones if op == "!="}
            if len(iguales) > 1:
                return None
            opciones = list(iguales) if iguales else info["valores"]
            v = next((x for x in opciones if x not in distintos), None)
            if v is None:
                return None
            ejemplo[clave] = v
    for p in sorted(activos):
        ejemplo[f"TIEMPO({p})"] = True
    return ejemplo


def describir(ejemplo) -> str:
    partes = []
    for clave, v in ejemplo.items():
        partes.append(clave if v is True else f"{clave} = {v}")
    return ", ".join(partes) if partes else "cualquier transacción"


def _primera_satisfacible(conjunciones):
    for c in conjunciones:
        e = satisfacible(c)
        if e is not None:
            return e
    return None


# =============================================================================
# 4. Análisis de las reglas
# =============================================================================

def _limpiar_condicion(nodo):
    """Condición del AST sin posiciones, para el objeto JSON."""
    if nodo is None:
        return None
    t = nodo["tipo"]
    if t in ("Y", "O"):
        return {"tipo": t, "operandos": [_limpiar_condicion(h) for h in nodo["operandos"]]}
    if t == "NO":
        return {"tipo": "NO", "operando": _limpiar_condicion(nodo["operando"])}
    if t == "tiempo":
        return {"tipo": "tiempo", "periodo": nodo["periodo"]}
    v = nodo["valor"]
    valor = int(v["texto"]) if v["token"] == "T_NUM" else v["texto"]
    return {"tipo": "comparacion", "objeto": nodo["objeto"], "atributo": nodo["atributo"],
            "operador": "==" if nodo["operador"] == "=" else nodo["operador"], "valor": valor}


def analizar(ast) -> dict:
    errores, advertencias, colisiones = [], [], []
    info_reglas = []

    for regla in ast:
        rid = regla["id"]
        errores_regla = []
        for rama in regla["ramas"]:
            if rama["condicion"] is not None:
                _validar_condicion(rama["condicion"], rid, errores_regla)
            d = rama["descuento"]
            if not 0 <= d["valor"] <= 100:
                errores_regla.append(_error("DESCUENTO_FUERA_DE_RANGO", rid, d,
                                            f"el descuento {d['texto']} está fuera del rango permitido (0% a 100%)."))

        efectivas = []  # por rama: lista de conjunciones satisfacibles
        if not errores_regla:
            try:
                previas = []
                for i, rama in enumerate(regla["ramas"]):
                    if rama["condicion"] is not None:
                        propia = fnn(rama["condicion"])
                        if _primera_satisfacible(fnd(propia)) is None:
                            errores_regla.append(_error(
                                "CONTRADICCION", rid, rama,
                                f"la condición de la rama {rama['tipo']} es contradictoria: nunca se cumple."))
                    else:
                        propia = None
                    partes = [fnd(_no(p)) for p in previas] + ([fnd(propia)] if propia else [])
                    efectiva = [c for c in _y(*partes) if satisfacible(c) is not None]
                    if not efectiva and not errores_regla:
                        advertencias.append(_error(
                            "RAMA_INALCANZABLE", rid, rama,
                            f"la rama {rama['tipo']} nunca se aplicará: las ramas anteriores ya cubren todos sus casos."))
                    efectivas.append(efectiva)
                    if propia:
                        previas.append(propia)
            except CondicionCompleja:
                advertencias.append(_error("CONDICION_COMPLEJA", rid, regla["ramas"][0],
                                           "la condición es demasiado compleja para verificar colisiones."))
                efectivas = []
        errores.extend(errores_regla)
        info_reglas.append({"regla": regla, "valida": not errores_regla, "efectivas": efectivas})

    # Colisiones: pares de reglas válidas con ramas que dan descuento y pueden cumplirse a la vez.
    for i, a in enumerate(info_reglas):
        for b in info_reglas[i + 1:]:
            if not (a["valida"] and b["valida"]) or not a["efectivas"] or not b["efectivas"]:
                continue
            for ia, ra in enumerate(a["regla"]["ramas"]):
                for ib, rb in enumerate(b["regla"]["ramas"]):
                    da, db = ra["descuento"]["valor"], rb["descuento"]["valor"]
                    if da == 0 or db == 0:
                        continue
                    ejemplo = None
                    for ca in a["efectivas"][ia]:
                        for cb in b["efectivas"][ib]:
                            ejemplo = satisfacible(ca + cb)
                            if ejemplo is not None:
                                break
                        if ejemplo is not None:
                            break
                    if ejemplo is None:
                        continue
                    ida, idb = a["regla"]["id"], b["regla"]["id"]
                    colisiones.append({
                        "reglas": [ida, idb],
                        "lineas": [ra["linea"], rb["linea"]],
                        "ramas": [ra["tipo"], rb["tipo"]],
                        "descuentos": [da, db],
                        "acumulado": da + db,
                        "duplicada": a["regla"]["texto"] == b["regla"]["texto"],
                        "ejemplo": describir(ejemplo),
                        "mensaje": (f"{ida} (línea {ra['linea']}, {ra['tipo']}, {da}%) y {idb} (línea {rb['linea']}, "
                                    f"{rb['tipo']}, {db}%) se aplican a la vez cuando {describir(ejemplo)}: "
                                    f"descuento acumulado de {da + db}%."),
                    })

    en_colision = {r for c in colisiones for r in c["reglas"]}
    reglas_json = []
    for info in info_reglas:
        r = info["regla"]
        estado = "rechazada" if not info["valida"] else ("en_colision" if r["id"] in en_colision else "aceptada")
        reglas_json.append({
            "id": r["id"],
            "linea": r["linea"],
            "texto": r["texto"],
            "estado": estado,
            "ramas": [{"tipo": ra["tipo"], "condicion": _limpiar_condicion(ra["condicion"]),
                       "descuento": ra["descuento"]["valor"]} for ra in r["ramas"]],
            "colisiona_con": sorted({x for c in colisiones if r["id"] in c["reglas"] for x in c["reglas"]} - {r["id"]}),
        })

    resumen = {
        "reglas": len(reglas_json),
        "aceptadas": sum(r["estado"] == "aceptada" for r in reglas_json),
        "en_colision": sum(r["estado"] == "en_colision" for r in reglas_json),
        "rechazadas": sum(r["estado"] == "rechazada" for r in reglas_json),
        "colisiones": len(colisiones),
    }
    return {
        "ok": not errores,
        "errores": errores,
        "advertencias": advertencias,
        "colisiones": colisiones,
        "objeto_json": {
            "lenguaje": "DSL de reglas de descuento",
            "version": "1.0",
            "listo_para_activar": not errores and not colisiones,
            "resumen": resumen,
            "reglas": reglas_json,
        },
    }
