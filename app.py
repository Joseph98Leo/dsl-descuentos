"""
Aplicación Flask del compilador DSL de reglas de descuento (USIL 2026-2).

Rutas
  GET  /                 Interfaz del compilador (analizador.html)
  GET  /hola             "Hola Mundo" de la Etapa 1 (index.html)
  POST /api/compilar     Compila las reglas: {"codigo": "..."} o un archivo en el campo "archivo"
  POST /api/tokens       Solo el análisis léxico (Etapa 1)
  GET  /api/automatas    ER, AFND, AFD y AFD mínimo de cada token (Etapa 2)
  GET  /api/catalogo     Catálogo de tokens y tabla de símbolos del dominio
"""

import os
from functools import lru_cache
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

import automatas
import compilador
import semantico
from lexer import CATALOGO, NOMBRE_CATEGORIA, analizar

BASE = Path(__file__).resolve().parent
EXTENSIONES = {".dsl", ".txt", ".reglas"}

app = Flask(__name__, static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024  # 256 KB por archivo
app.json.ensure_ascii = False


def _leer_entrada():
    """Obtiene el código fuente del archivo subido, del JSON o del formulario."""
    archivo = request.files.get("archivo")
    if archivo and archivo.filename:
        if Path(archivo.filename).suffix.lower() not in EXTENSIONES:
            return None, f"El archivo «{archivo.filename}» no es válido. Sube un archivo .dsl, .txt o .reglas."
        try:
            return archivo.read().decode("utf-8"), None
        except UnicodeDecodeError:
            return None, "El archivo no está en UTF-8. Guárdalo como texto UTF-8 e inténtalo de nuevo."
    datos = request.get_json(silent=True) or {}
    return datos.get("codigo", request.form.get("codigo", "")), None


@app.get("/")
def inicio():
    return send_from_directory(BASE, "analizador.html")


@app.get("/analizador.html")
def analizador():
    return send_from_directory(BASE, "analizador.html")


@app.get("/hola")
def hola():
    return send_from_directory(BASE, "index.html")


@app.get("/ejemplos/<path:nombre>")
def ejemplos(nombre):
    return send_from_directory(BASE / "ejemplos", nombre, mimetype="text/plain")


@app.post("/api/compilar")
def api_compilar():
    texto, error = _leer_entrada()
    if error:
        return jsonify(error=error), 400
    return jsonify(compilador.compilar(texto))


@app.post("/api/tokens")
def api_tokens():
    texto, error = _leer_entrada()
    if error:
        return jsonify(error=error), 400
    tokens, errores = analizar(texto)
    return jsonify(tokens=[t.to_dict() for t in tokens], errores=errores)


@lru_cache(maxsize=1)
def _automatas():
    return {"tokens": automatas.automatas_de_tokens()}


@app.get("/api/automatas")
def api_automatas():
    return jsonify(_automatas())


@app.get("/api/catalogo")
def api_catalogo():
    return jsonify(catalogo=CATALOGO, nombres=NOMBRE_CATEGORIA, dominio=semantico.DOMINIO)


@app.errorhandler(413)
def archivo_grande(_):
    return jsonify(error="El archivo supera el límite de 256 KB."), 413


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
