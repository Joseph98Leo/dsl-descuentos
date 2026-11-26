#!/usr/bin/env bash
# Genera el analizador léxico y sintáctico en Python a partir de la gramática
# gramatica/ReglasDescuento.g4 con el metacompilador ANTLR 4.13.2.
#
# Requisitos: Java 11 o superior. El .jar de ANTLR se descarga de Maven Central
# la primera vez y se guarda en herramientas/.
#
# Uso:  bash herramientas/generar_parser.sh
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="4.13.2"
JAR="$RAIZ/herramientas/antlr-$VERSION-complete.jar"
URL="https://repo1.maven.org/maven2/org/antlr/antlr4/$VERSION/antlr4-$VERSION-complete.jar"

if [ ! -f "$JAR" ]; then
  echo "Descargando ANTLR $VERSION desde Maven Central..."
  curl -fsSL -o "$JAR" "$URL"
fi

cd "$RAIZ/gramatica"
java -jar "$JAR" -Dlanguage=Python3 -visitor -no-listener -o "$RAIZ/generado" -Xexact-output-dir ReglasDescuento.g4
touch "$RAIZ/generado/__init__.py"

echo "Analizador generado en: $RAIZ/generado"
ls "$RAIZ/generado"
