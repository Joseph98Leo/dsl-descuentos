"""
Compilador del DSL de reglas de descuento: integra todas las fases.

    texto ─► léxico (lexer.py) ─► sintáctico (ANTLR) ─► semántico ─► objeto JSON

Cada fase solo se ejecuta si la anterior terminó sin errores, como en un
compilador real. El resultado es un diccionario serializable a JSON que usan
tanto la aplicación Flask (app.py) como la versión del navegador (Pyodide).
"""

from __future__ import annotations

import json
import time

import lexer
import semantico
import sintactico


def _ms(inicio):
    return round((time.perf_counter() - inicio) * 1000, 2)


def compilar(texto: str) -> dict:
    tiempos = {}

    t = time.perf_counter()
    tokens, errores_lexicos = lexer.analizar(texto)
    resultado = {
        "lexico": {
            "ok": not errores_lexicos,
            "tokens": [tk.to_dict() for tk in tokens],
            "errores": errores_lexicos,
            "resumen": [[tok, info] for tok, info in lexer.resumen(tokens)],
            "lineas": lexer.resaltar(texto),
        },
        "sintactico": None,
        "semantico": None,
    }
    tiempos["lexico"] = _ms(t)

    if errores_lexicos:
        resultado["fase_con_error"] = "léxico"
    else:
        t = time.perf_counter()
        sint = sintactico.analizar(texto)
        tiempos["sintactico"] = _ms(t)
        ast = sint.pop("ast")
        resultado["sintactico"] = sint
        if not sint["ok"]:
            resultado["fase_con_error"] = "sintáctico"
        else:
            t = time.perf_counter()
            sem = semantico.analizar(ast)
            tiempos["semantico"] = _ms(t)
            resultado["semantico"] = sem
            resultado["fase_con_error"] = None if sem["ok"] else "semántico"

    tiempos["total"] = round(sum(tiempos.values()), 2)
    resultado["tiempos_ms"] = tiempos
    resultado["aceptado"] = resultado["fase_con_error"] is None
    return resultado


def compilar_json(texto: str) -> str:
    return json.dumps(compilar(texto), ensure_ascii=False)


if __name__ == "__main__":
    import sys

    fuente = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    r = compilar(fuente)
    if not r["aceptado"]:
        fase = r["fase_con_error"]
        errores = {"léxico": r["lexico"]["errores"],
                   "sintáctico": [e["mensaje"] for e in (r["sintactico"] or {}).get("errores", [])],
                   "semántico": [e["mensaje"] for e in (r["semantico"] or {}).get("errores", [])]}[fase]
        print(f"Error {fase}:")
        for e in errores:
            print("  -", e)
    if r["semantico"]:
        for a in r["semantico"]["advertencias"]:
            print("Advertencia:", a["mensaje"])
        for c in r["semantico"]["colisiones"]:
            print("Colisión:", c["mensaje"])
        print(json.dumps(r["semantico"]["objeto_json"], ensure_ascii=False, indent=2))
    print(f"Tiempos (ms): {r['tiempos_ms']}")
