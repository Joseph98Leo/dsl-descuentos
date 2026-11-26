"""
Evaluación de la solución: calcula las métricas de los objetivos específicos y
las guarda en resultados/metricas.json y resultados/metricas.md (para la
sección de Resultados del informe).

  OE1  Número de tokens modelados (ER, AFND, AFD, quíntupla).
  OE2  Cadenas de prueba reconocidas o rechazadas correctamente por el
       analizador léxico y sintáctico generado con ANTLR.
  OE3  Porcentaje de solapamientos configurados que detecta el análisis
       semántico, y falsos positivos.
  OE4  Objetos JSON generados (uno por regla de cada cadena aceptada).
  OE5  Tasa de éxito de las pruebas automatizadas (pytest).
  RNF  Tiempo de análisis por regla (debe ser menor a 200 ms).

Uso:  python evaluar.py
"""

import json
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import automatas
import compilador

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / "resultados"


def oe1():
    datos = automatas.automatas_de_tokens()
    return {
        "tokens": len(datos),
        "detalle": [{"token": t["token"], "er": t["er"], "afnd": t["afnd"]["estados"],
                     "afd": t["afd"]["estados"], "minimo": t["minimo"]["estados"]} for t in datos],
    }


def oe2_oe4(cadenas):
    aceptadas_ok, detalle = 0, []
    objetos_json = 0
    for c in cadenas["aceptadas"]:
        r = compilador.compilar(c)
        ok = r["sintactico"] is not None and r["sintactico"]["ok"]
        aceptadas_ok += ok
        if r["semantico"]:
            objetos_json += len(r["semantico"]["objeto_json"]["reglas"])
        detalle.append({"cadena": c, "esperado": "aceptada", "obtenido": "aceptada" if ok else r["fase_con_error"], "ok": ok})
    rechazadas_ok = 0
    for caso in cadenas["rechazadas"]:
        r = compilador.compilar(caso["cadena"])
        ok = r["fase_con_error"] == caso["fase"]
        rechazadas_ok += ok
        detalle.append({"cadena": caso["cadena"], "esperado": f"rechazada ({caso['fase']})",
                        "obtenido": f"rechazada ({r['fase_con_error']})" if r["fase_con_error"] else "aceptada", "ok": ok})
    total = len(cadenas["aceptadas"]) + len(cadenas["rechazadas"])
    return {
        "aceptadas": {"total": len(cadenas["aceptadas"]), "correctas": aceptadas_ok},
        "rechazadas": {"total": len(cadenas["rechazadas"]), "correctas": rechazadas_ok},
        "exactitud": round(100 * (aceptadas_ok + rechazadas_ok) / total, 2),
        "detalle": detalle,
    }, objetos_json


def oe3(casos):
    esperadas_total = detectadas = falsos_positivos = 0
    detalle = []
    for caso in casos:
        r = compilador.compilar(caso["reglas"])
        encontradas = {tuple(c["reglas"]) for c in (r["semantico"] or {}).get("colisiones", [])}
        esperadas = {tuple(p) for p in caso["esperadas"]}
        esperadas_total += len(esperadas)
        detectadas += len(encontradas & esperadas)
        falsos_positivos += len(encontradas - esperadas)
        detalle.append({"caso": caso["nombre"], "esperadas": len(esperadas),
                        "detectadas": len(encontradas & esperadas), "falsos_positivos": len(encontradas - esperadas)})
    return {
        "casos": len(casos),
        "solapamientos_configurados": esperadas_total,
        "detectados": detectadas,
        "tasa_deteccion": round(100 * detectadas / esperadas_total, 2) if esperadas_total else None,
        "falsos_positivos": falsos_positivos,
        "detalle": detalle,
    }


def rendimiento(cadenas, repeticiones=20):
    tiempos = []
    for c in cadenas["aceptadas"]:
        r = compilador.compilar(c)
        reglas = len(r["sintactico"]["reglas"])
        for _ in range(repeticiones):
            tiempos.append(compilador.compilar(c)["tiempos_ms"]["total"] / reglas)
    return {"muestras": len(tiempos), "promedio_ms": round(statistics.mean(tiempos), 2),
            "p95_ms": round(sorted(tiempos)[int(0.95 * len(tiempos)) - 1], 2), "maximo_ms": round(max(tiempos), 2),
            "limite_ms": 200, "cumple": max(tiempos) < 200}


def oe5():
    proceso = subprocess.run([sys.executable, "-m", "pytest", "-q", "--junitxml", str(SALIDA / "pytest.xml")],
                             cwd=RAIZ, capture_output=True, text=True)
    import xml.etree.ElementTree as ET
    suite = ET.parse(SALIDA / "pytest.xml").getroot()
    suite = suite if suite.tag == "testsuite" else suite.find("testsuite")
    total = int(suite.get("tests"))
    fallidas = int(suite.get("failures")) + int(suite.get("errors"))
    omitidas = int(suite.get("skipped"))
    exitosas = total - fallidas - omitidas
    return {"total": total, "exitosas": exitosas, "fallidas": fallidas, "omitidas": omitidas,
            "tasa_exito": round(100 * exitosas / total, 2), "salida": proceso.stdout.strip().splitlines()[-1]}


def main():
    SALIDA.mkdir(exist_ok=True)
    cadenas = json.loads((RAIZ / "casos" / "cadenas.json").read_text(encoding="utf-8"))
    casos = json.loads((RAIZ / "casos" / "colisiones.json").read_text(encoding="utf-8"))["casos"]

    m_oe2, objetos = oe2_oe4(cadenas)
    metricas = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "OE1": oe1(),
        "OE2": m_oe2,
        "OE3": oe3(casos),
        "OE4": {"objetos_json_generados": objetos},
        "OE5": oe5(),
        "RNF_rendimiento": rendimiento(cadenas),
    }
    (SALIDA / "metricas.json").write_text(json.dumps(metricas, ensure_ascii=False, indent=2), encoding="utf-8")

    o1, o2, o3, o5, rn = metricas["OE1"], metricas["OE2"], metricas["OE3"], metricas["OE5"], metricas["RNF_rendimiento"]
    md = [
        "# Resultados de la evaluación",
        "",
        f"Generado el {metricas['fecha']} con `python evaluar.py`.",
        "",
        "| Objetivo | Indicador | Meta | Resultado |",
        "|---|---|---|---|",
        f"| OE1 | Tokens modelados (ER, AFND, AFD, quíntupla) | ≥ 15 | {o1['tokens']} |",
        f"| OE2 | Cadenas de prueba clasificadas correctamente | ≥ 5 cadenas | {o2['aceptadas']['correctas'] + o2['rechazadas']['correctas']} de "
        f"{o2['aceptadas']['total'] + o2['rechazadas']['total']} ({o2['exactitud']} %) |",
        f"| OE3 | Solapamientos configurados detectados | ≥ 90 % | {o3['detectados']} de {o3['solapamientos_configurados']} "
        f"({o3['tasa_deteccion']} %), {o3['falsos_positivos']} falsos positivos |",
        f"| OE4 | Objetos JSON generados | uno por regla | {metricas['OE4']['objetos_json_generados']} |",
        f"| OE5 | Pruebas automatizadas exitosas | > 95 % | {o5['exitosas']} de {o5['total']} ({o5['tasa_exito']} %) |",
        f"| RNF | Tiempo de análisis por regla | < 200 ms | promedio {rn['promedio_ms']} ms, máximo {rn['maximo_ms']} ms |",
        "",
        "## OE1 · Autómatas por token",
        "",
        "| Token | Expresión regular | Estados AFND | Estados AFD | Estados AFD mínimo |",
        "|---|---|---|---|---|",
    ]
    md += [f"| {d['token']} | `{d['er'].replace('|', chr(92) + '|')}` | {d['afnd']} | {d['afd']} | {d['minimo']} |" for d in o1["detalle"]]
    md += ["", "## OE2 · Cadenas de prueba", "", "| Cadena | Esperado | Obtenido | Correcto |", "|---|---|---|---|"]
    md += [f"| `{d['cadena'].replace(chr(10), ' ⏎ ').replace('|', chr(92) + '|')}` | {d['esperado']} | {d['obtenido']} | {'Sí' if d['ok'] else 'No'} |"
           for d in o2["detalle"]]
    md += ["", "## OE3 · Detección de colisiones", "", "| Caso | Esperadas | Detectadas | Falsos positivos |", "|---|---|---|---|"]
    md += [f"| {d['caso']} | {d['esperadas']} | {d['detectadas']} | {d['falsos_positivos']} |" for d in o3["detalle"]]
    (SALIDA / "metricas.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print("\n".join(md[:13]))
    print(f"\nDetalle completo en {SALIDA / 'metricas.md'}")


if __name__ == "__main__":
    main()
