"""
Etapa 2 — Autómatas finitos generados desde el código.

Para cada token del lenguaje, a partir de su expresión regular (la misma del
catálogo de lexer.py y del informe, sección 8.2.1) se construye:

  1. El AFND con el método de Thompson (con transiciones ε).
  2. El AFD equivalente con el método de subconjuntos (cerradura-ε + mover).
  3. El AFD mínimo con el algoritmo de partición de estados (Moore).

De cada autómata se obtiene la quíntupla M = (Q, Σ, δ, q0, F), la tabla de
transiciones y el gráfico en lenguaje DOT (Graphviz). El gráfico no es una
imagen: se dibuja a partir de este código.

Notación del informe: L = [a-zA-Z] y D = [0-9] son abreviaturas de clases de
caracteres. Solo se interpretan como clases en los tokens que las usan
(T_ID, T_NUM y T_PORCENTAJE); en las palabras reservadas, L y D son letras.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from lexer import CATALOGO

EPSILON = "ε"

# Tokens cuya expresión regular usa las clases L y D.
TOKENS_CON_CLASES = {"T_ID", "T_NUM", "T_PORCENTAJE"}


# =============================================================================
# 1. Análisis de la expresión regular
# =============================================================================
#
#   union   → concat ('|' concat)*
#   concat  → postfijo postfijo*
#   postfijo→ atomo ('*' | '+' | '?')*
#   atomo   → símbolo | '\' carácter | '(' union ')'

class ErrorER(ValueError):
    pass


class _LectorER:
    def __init__(self, texto: str, clases: bool):
        self.s = texto.replace(" ", "")
        self.i = 0
        self.clases = clases

    def ver(self):
        return self.s[self.i] if self.i < len(self.s) else None

    def tomar(self):
        c = self.ver()
        self.i += 1
        return c

    def analizar(self):
        nodo = self.union()
        if self.ver() is not None:
            raise ErrorER(f"Carácter inesperado «{self.ver()}» en la posición {self.i}")
        return nodo

    def union(self):
        ramas = [self.concat()]
        while self.ver() == "|":
            self.tomar()
            ramas.append(self.concat())
        return ramas[0] if len(ramas) == 1 else ("union", ramas)

    def concat(self):
        partes = []
        while self.ver() is not None and self.ver() not in "|)":
            partes.append(self.postfijo())
        if not partes:
            raise ErrorER(f"Expresión vacía en la posición {self.i}")
        return partes[0] if len(partes) == 1 else ("concat", partes)

    def postfijo(self):
        nodo = self.atomo()
        while self.ver() in ("*", "+", "?"):
            nodo = ({"*": "estrella", "+": "mas", "?": "opcional"}[self.tomar()], nodo)
        return nodo

    def atomo(self):
        c = self.tomar()
        if c == "(":
            nodo = self.union()
            if self.tomar() != ")":
                raise ErrorER("Falta cerrar un paréntesis")
            return nodo
        if c == "\\":
            return ("simbolo", self.tomar())
        if c is None or c in "|)*+?":
            raise ErrorER(f"Símbolo inesperado «{c}»")
        return ("simbolo", c)


def analizar_er(er: str, clases: bool = False):
    """Convierte la ER en un árbol: ('simbolo', c), ('concat', [...]), ('union', [...]), ('estrella', n)…"""
    return _LectorER(er, clases).analizar()


# =============================================================================
# 2. AFND por el método de Thompson
# =============================================================================

@dataclass
class AFND:
    estados: list
    alfabeto: list
    transiciones: dict          # (estado, símbolo) -> set(estados); símbolo puede ser ε
    inicial: str
    finales: set


class _Thompson:
    """Construye fragmentos (inicio, fin). Un fragmento de Thompson nunca tiene
    transiciones que entren a su inicio ni que salgan de su fin, por eso la
    concatenación puede fusionar el fin del primero con el inicio del segundo
    (así 'SI' queda como q0 -S-> q1 -I-> q2, igual que en el informe)."""

    def __init__(self):
        self.n = 0
        self.trans = {}         # estado -> list[(símbolo, destino)]

    def nuevo(self):
        e = self.n
        self.n += 1
        self.trans[e] = []
        return e

    def arco(self, a, simbolo, b):
        self.trans[a].append((simbolo, b))

    def fusionar(self, fin_a, inicio_b):
        self.trans[fin_a].extend(self.trans.pop(inicio_b))
        for origen, arcos in self.trans.items():
            self.trans[origen] = [(s, fin_a if d == inicio_b else d) for s, d in arcos]

    def construir(self, nodo):
        tipo = nodo[0]
        if tipo == "simbolo":
            a, b = self.nuevo(), self.nuevo()
            self.arco(a, nodo[1], b)
            return a, b
        if tipo == "concat":
            inicio, fin = self.construir(nodo[1][0])
            for parte in nodo[1][1:]:
                i2, f2 = self.construir(parte)
                self.fusionar(fin, i2)
                fin = f2
            return inicio, fin
        if tipo == "union":
            a = self.nuevo()
            fragmentos = [self.construir(r) for r in nodo[1]]
            b = self.nuevo()
            for i, f in fragmentos:
                self.arco(a, EPSILON, i)
                self.arco(f, EPSILON, b)
            return a, b
        if tipo in ("estrella", "mas", "opcional"):
            a = self.nuevo()
            i, f = self.construir(nodo[1])
            b = self.nuevo()
            self.arco(a, EPSILON, i)
            if tipo in ("estrella", "mas"):
                self.arco(f, EPSILON, i)        # repetir
            self.arco(f, EPSILON, b)
            if tipo in ("estrella", "opcional"):
                self.arco(a, EPSILON, b)        # cero veces
            return a, b
        raise ErrorER(f"Nodo desconocido: {tipo}")


def thompson(er: str, clases: bool = False) -> AFND:
    t = _Thompson()
    inicio, fin = t.construir(analizar_er(er, clases))

    # Renombrar en orden de recorrido (BFS) desde el inicio: q0, q1, q2, …
    orden, cola, vistos = [], [inicio], {inicio}
    while cola:
        e = cola.pop(0)
        orden.append(e)
        for _, d in t.trans[e]:
            if d not in vistos:
                vistos.add(d)
                cola.append(d)
    nombre = {e: f"q{i}" for i, e in enumerate(orden)}

    transiciones, alfabeto = {}, []
    for e in orden:
        for s, d in t.trans[e]:
            transiciones.setdefault((nombre[e], s), set()).add(nombre[d])
            if s != EPSILON and s not in alfabeto:
                alfabeto.append(s)

    return AFND(
        estados=[nombre[e] for e in orden],
        alfabeto=alfabeto,
        transiciones=transiciones,
        inicial=nombre[inicio],
        finales={nombre[fin]},
    )


# =============================================================================
# 3. AFD por el método de subconjuntos
# =============================================================================

@dataclass
class AFD:
    estados: list
    alfabeto: list
    transiciones: dict          # (estado, símbolo) -> estado
    inicial: str
    finales: set
    subconjuntos: dict = field(default_factory=dict)   # estado -> estados del autómata anterior


def _orden_estado(nombre):
    return int(nombre[1:]) if nombre[1:].isdigit() else 10**9


def cerradura_epsilon(afnd: AFND, estados) -> frozenset:
    pila, resultado = list(estados), set(estados)
    while pila:
        e = pila.pop()
        for d in afnd.transiciones.get((e, EPSILON), ()):
            if d not in resultado:
                resultado.add(d)
                pila.append(d)
    return frozenset(resultado)


def mover(afnd: AFND, estados, simbolo) -> set:
    destino = set()
    for e in estados:
        destino |= afnd.transiciones.get((e, simbolo), set())
    return destino


def subconjuntos(afnd: AFND) -> AFD:
    inicio = cerradura_epsilon(afnd, {afnd.inicial})
    nombres, orden, pendientes = {inicio: "q0"}, [inicio], [inicio]
    transiciones = {}
    while pendientes:
        actual = pendientes.pop(0)
        for s in afnd.alfabeto:
            destino = cerradura_epsilon(afnd, mover(afnd, actual, s))
            if not destino:
                continue                         # estado de error: se omite ("-" en la tabla)
            if destino not in nombres:
                nombres[destino] = f"q{len(nombres)}"
                orden.append(destino)
                pendientes.append(destino)
            transiciones[(nombres[actual], s)] = nombres[destino]

    return AFD(
        estados=[nombres[c] for c in orden],
        alfabeto=list(afnd.alfabeto),
        transiciones=transiciones,
        inicial="q0",
        finales={nombres[c] for c in orden if c & afnd.finales},
        subconjuntos={nombres[c]: sorted(c, key=_orden_estado) for c in orden},
    )


# =============================================================================
# 4. Minimización (partición de estados)
# =============================================================================

def minimizar(afd: AFD) -> AFD:
    SUMIDERO = "∅"
    estados = list(afd.estados) + [SUMIDERO]

    def delta(e, s):
        return afd.transiciones.get((e, s), SUMIDERO) if e != SUMIDERO else SUMIDERO

    # Partición inicial: finales / no finales. Se refina hasta que no cambie.
    clase = {e: (1 if e in afd.finales else 0) for e in estados}
    while True:
        firmas = {e: (clase[e],) + tuple(clase[delta(e, s)] for s in afd.alfabeto) for e in estados}
        nuevas = {}
        for e in estados:
            nuevas.setdefault(firmas[e], len(nuevas))
        nueva_clase = {e: nuevas[firmas[e]] for e in estados}
        if len(set(nueva_clase.values())) == len(set(clase.values())):
            break
        clase = nueva_clase

    muertos = {clase[SUMIDERO]}
    # Renombrar los bloques en orden de recorrido desde el inicial.
    nombres, orden, cola = {}, [], [clase[afd.inicial]]
    while cola:
        b = cola.pop(0)
        if b in nombres or b in muertos:
            continue
        nombres[b] = f"q{len(nombres)}"
        orden.append(b)
        representante = next(e for e in afd.estados if clase[e] == b)
        for s in afd.alfabeto:
            cola.append(clase[delta(representante, s)])

    transiciones = {}
    for b in orden:
        representante = next(e for e in afd.estados if clase[e] == b)
        for s in afd.alfabeto:
            d = clase[delta(representante, s)]
            if d not in muertos:
                transiciones[(nombres[b], s)] = nombres[d]

    return AFD(
        estados=[nombres[b] for b in orden],
        alfabeto=list(afd.alfabeto),
        transiciones=transiciones,
        inicial=nombres[clase[afd.inicial]],
        finales={nombres[b] for b in orden if any(clase[e] == b for e in afd.finales)},
        subconjuntos={nombres[b]: sorted((e for e in afd.estados if clase[e] == b), key=_orden_estado) for b in orden},
    )


# =============================================================================
# 5. Simulación
# =============================================================================

def simbolo_de(caracter: str, clases: bool) -> str:
    """Traduce un carácter al símbolo del alfabeto del autómata (L, D o el propio carácter)."""
    if clases:
        if caracter.isascii() and caracter.isalpha():
            return "L"
        if caracter.isascii() and caracter.isdigit():
            return "D"
    return caracter


def acepta(afd: AFD, cadena: str, clases: bool = False) -> bool:
    estado = afd.inicial
    for c in cadena:
        estado = afd.transiciones.get((estado, simbolo_de(c, clases)))
        if estado is None:
            return False
    return estado in afd.finales


def recorrido(afd: AFD, cadena: str, clases: bool = False):
    """Secuencia de estados visitados (para mostrar la traza en la interfaz)."""
    estado, pasos = afd.inicial, [afd.inicial]
    for c in cadena:
        estado = afd.transiciones.get((estado, simbolo_de(c, clases)))
        if estado is None:
            pasos.append("-")
            break
        pasos.append(estado)
    return pasos


# =============================================================================
# 6. Presentación: quíntupla, tabla y DOT
# =============================================================================

def _conjunto(elementos):
    return "{" + ", ".join(elementos) + "}"


def quintupla(automata) -> dict:
    es_afnd = isinstance(automata, AFND)
    delta = []
    for (e, s), d in sorted(automata.transiciones.items(), key=lambda x: (_orden_estado(x[0][0]), x[0][1])):
        destinos = sorted(d, key=_orden_estado) if es_afnd else [d]
        for destino in destinos:
            delta.append(f"δ({e}, {s}) = {destino}")
    return {
        "Q": _conjunto(automata.estados),
        "Σ": _conjunto(automata.alfabeto),
        "δ": delta,
        "q0": automata.inicial,
        "F": _conjunto(sorted(automata.finales, key=_orden_estado)),
    }


def tabla(automata) -> dict:
    es_afnd = isinstance(automata, AFND)
    columnas = list(automata.alfabeto)
    if es_afnd and any(s == EPSILON for _, s in automata.transiciones):
        columnas.append(EPSILON)
    filas = []
    for e in automata.estados:
        celdas = []
        for s in columnas:
            d = automata.transiciones.get((e, s))
            if not d:
                celdas.append("-")
            elif es_afnd:
                celdas.append(", ".join(sorted(d, key=_orden_estado)))
            else:
                celdas.append(d)
        marca = ("→" if e == automata.inicial else "") + ("*" if e in automata.finales else "")
        filas.append({"estado": e, "marca": marca, "celdas": celdas})
    return {"columnas": columnas, "filas": filas}


def _escapar_dot(texto: str) -> str:
    return texto.replace("\\", "\\\\").replace('"', '\\"')


def dot(automata, titulo: str = "") -> str:
    """Gráfico del autómata en lenguaje DOT (lo dibuja Graphviz / viz.js)."""
    es_afnd = isinstance(automata, AFND)
    lineas = [
        "digraph automata {",
        '  rankdir=LR; bgcolor="transparent"; pad=0.2;',
        '  node [shape=circle, fontname="IBM Plex Mono", fontsize=12, color="#5b5045", fontcolor="#2b241d", width=0.45, fixedsize=true];',
        '  edge [fontname="IBM Plex Mono", fontsize=11, color="#7a6e62", fontcolor="#2b241d", arrowsize=0.7];',
        '  inicio [shape=point, width=0.08, color="#2b241d"];',
    ]
    if titulo:
        lineas.append(f'  label="{_escapar_dot(titulo)}"; labelloc=t; fontname="IBM Plex Sans"; fontsize=13; fontcolor="#5b5045";')
    for e in automata.estados:
        forma = "doublecircle" if e in automata.finales else "circle"
        lineas.append(f'  "{e}" [shape={forma}];')
    lineas.append(f'  inicio -> "{automata.inicial}";')

    # Agrupar símbolos con el mismo origen y destino en una sola flecha.
    etiquetas = {}
    for (e, s), d in automata.transiciones.items():
        for destino in (sorted(d, key=_orden_estado) if es_afnd else [d]):
            etiquetas.setdefault((e, destino), []).append(s)
    for (e, d), simbolos in etiquetas.items():
        texto = ", ".join(simbolos)
        estilo = ', style=dashed, color="#a1958a"' if simbolos == [EPSILON] else ""
        lineas.append(f'  "{e}" -> "{d}" [label="{_escapar_dot(texto)}"{estilo}];')
    lineas.append("}")
    return "\n".join(lineas)


# =============================================================================
# 7. Todos los tokens del lenguaje
# =============================================================================

def _serializar(automata, titulo, con_subconjuntos=False):
    datos = {
        "estados": len(automata.estados),
        "quintupla": quintupla(automata),
        "tabla": tabla(automata),
        "dot": dot(automata, titulo),
    }
    if con_subconjuntos:
        datos["subconjuntos"] = automata.subconjuntos
    return datos


def construir_token(token: str, er: str):
    clases = token in TOKENS_CON_CLASES
    afnd = thompson(er, clases)
    afd = subconjuntos(afnd)
    minimo = minimizar(afd)
    return afnd, afd, minimo, clases


def automatas_de_tokens():
    """Construye ER → AFND → AFD → AFD mínimo para cada token del catálogo."""
    resultado = []
    for token, categoria, ejemplos, er in CATALOGO:
        afnd, afd, minimo, clases = construir_token(token, er)
        resultado.append({
            "token": token,
            "categoria": categoria,
            "er": er,
            "ejemplos": ejemplos,
            "clases": clases,
            "afnd": _serializar(afnd, f"AFND de {token}"),
            "afd": _serializar(afd, f"AFD de {token}", con_subconjuntos=True),
            "minimo": _serializar(minimo, f"AFD mínimo de {token}", con_subconjuntos=True),
        })
    return resultado


def automatas_json() -> str:
    return json.dumps({"tokens": automatas_de_tokens()}, ensure_ascii=False)


if __name__ == "__main__":
    for t in automatas_de_tokens():
        print(f"{t['token']:<14} ER: {t['er']:<28} AFND {t['afnd']['estados']:>2}  "
              f"AFD {t['afd']['estados']:>2}  mínimo {t['minimo']['estados']:>2}")
