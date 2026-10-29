"""
Aplicación Flask - Etapa 1 del Trabajo Final de Compiladores (USIL 2026-2).

Permite escribir o subir un archivo con reglas del DSL de descuentos y muestra
los TOKENS y LEXEMAS que reconoce el analizador léxico.
"""

import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from lexer import CATALOGO, NOMBRE_CATEGORIA, analizar, resaltar, resumen

BASE = Path(__file__).resolve().parent
EJEMPLO = (BASE / "ejemplos" / "reglas_ejemplo.dsl").read_text(encoding="utf-8")
EXTENSIONES = {".dsl", ".txt", ".reglas"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024  # 256 KB por archivo


def _leer_entrada():
    """Obtiene el código fuente desde el archivo subido o desde el cuadro de texto."""
    archivo = request.files.get("archivo")
    if archivo and archivo.filename:
        extension = Path(archivo.filename).suffix.lower()
        if extension not in EXTENSIONES:
            return None, archivo.filename, (
                f"El archivo «{archivo.filename}» no es válido. Sube un archivo .dsl, .txt o .reglas."
            )
        try:
            return archivo.read().decode("utf-8"), archivo.filename, None
        except UnicodeDecodeError:
            return None, archivo.filename, "El archivo no está en UTF-8. Guárdalo como texto UTF-8 e inténtalo de nuevo."
    return request.form.get("codigo", ""), None, None


@app.route("/", methods=["GET", "POST"])
def inicio():
    codigo, nombre_archivo, error_entrada, resultado = EJEMPLO, None, None, None

    if request.method == "POST":
        texto, nombre_archivo, error_entrada = _leer_entrada()
        if texto is not None:
            codigo = texto
            if not codigo.strip():
                error_entrada = "No hay nada que analizar: escribe una regla o sube un archivo."
            else:
                tokens, errores = analizar(codigo)
                resultado = {
                    "tokens": tokens,
                    "errores": errores,
                    "resumen": resumen(tokens),
                    "lineas": resaltar(codigo),
                }

    return render_template(
        "index.html",
        codigo=codigo,
        ejemplo=EJEMPLO,
        nombre_archivo=nombre_archivo,
        error_entrada=error_entrada,
        resultado=resultado,
        catalogo=CATALOGO,
        nombres=NOMBRE_CATEGORIA,
    )


@app.post("/api/tokens")
def api_tokens():
    """Versión JSON del análisis: recibe {"codigo": "..."}."""
    datos = request.get_json(silent=True) or {}
    tokens, errores = analizar(datos.get("codigo", ""))
    return jsonify(tokens=[t.to_dict() for t in tokens], errores=errores)


@app.errorhandler(413)
def archivo_grande(_):
    return render_template(
        "index.html",
        codigo=EJEMPLO,
        ejemplo=EJEMPLO,
        nombre_archivo=None,
        error_entrada="El archivo supera el límite de 256 KB.",
        resultado=None,
        catalogo=CATALOGO,
        nombres=NOMBRE_CATEGORIA,
    ), 413


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
