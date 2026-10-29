"""
Analizador léxico del DSL de reglas de descuento.

Recorre la cadena de entrada de izquierda a derecha aplicando la regla de la
coincidencia más larga (maximal munch) y clasifica cada lexema en su token,
según la tabla de lexemas/tokens/expresiones regulares del informe (8.2.1).
"""

import re
from dataclasses import dataclass, asdict

# Palabras reservadas: se reconocen primero como identificador (L|_)(L|D|_)*
# y luego se buscan en esta tabla, igual que hace un lexer real.
PALABRAS_RESERVADAS = {
    "SI": "T_SI",
    "SINO": "T_SINO",
    "ENTONCES": "T_ENTONCES",
    "APLICAR": "T_APLICAR",
    "DESCUENTO": "T_DESCUENTO",
    "Y": "T_AND",
    "O": "T_OR",
    "NO": "T_NOT",
    "CLIENTE": "T_OBJETO",
    "COMPRA": "T_OBJETO",
    "TIEMPO": "T_TIEMPO",
}

# Catálogo de tokens: descripción, categoría y expresión regular (notación del informe).
CATALOGO = [
    # token,          categoría,             ejemplo de lexema,               expresión regular
    ("T_SI",          "reservada",   "SI",                            "SI"),
    ("T_SINO",        "reservada",   "SINO",                          "SINO"),
    ("T_ENTONCES",    "reservada",   "ENTONCES",                      "ENTONCES"),
    ("T_APLICAR",     "reservada",   "APLICAR",                       "APLICAR"),
    ("T_DESCUENTO",   "reservada",   "DESCUENTO",                     "DESCUENTO"),
    ("T_AND",         "logico",      "Y",                             "Y"),
    ("T_OR",          "logico",      "O",                             "O"),
    ("T_NOT",         "logico",      "NO",                            "NO"),
    ("T_OBJETO",      "objeto",      "CLIENTE, COMPRA",               "(CLIENTE|COMPRA)"),
    ("T_TIEMPO",      "reservada",   "TIEMPO",                        "TIEMPO"),
    ("T_ID",          "identificador", "nivel, total, VIP",           "(L|_)(L|D|_)*"),
    ("T_NUM",         "literal",     "500, 20",                       "D+"),
    ("T_PORCENTAJE",  "literal",     "15%",                           "D+%"),
    ("T_RELOP",       "relacional",  "=, ==, !=, >, >=, <, <=",       "= | == | != | >(=)? | <(=)?"),
    ("T_PUNTO",       "delimitador", ".",                             "\\."),
    ("T_PARI",        "delimitador", "(",                             "\\("),
    ("T_PARD",        "delimitador", ")",                             "\\)"),
]

CATEGORIA = {token: categoria for token, categoria, _, _ in CATALOGO}
CATEGORIA["T_ERROR"] = "error"

NOMBRE_CATEGORIA = {
    "reservada": "Palabra reservada",
    "logico": "Operador lógico",
    "objeto": "Objeto del dominio",
    "identificador": "Identificador",
    "literal": "Literal",
    "relacional": "Operador relacional",
    "delimitador": "Delimitador",
    "error": "Error léxico",
}

# El orden importa: T_PORCENTAJE antes que T_NUM y los operadores de dos
# caracteres antes que los de uno, para respetar la coincidencia más larga.
_PATRONES = [
    ("COMENTARIO",   r"//[^\n]*"),
    ("ESPACIO",      r"[ \t\r]+"),
    ("SALTO",        r"\n"),
    ("T_PORCENTAJE", r"[0-9]+%"),
    ("T_NUM",        r"[0-9]+"),
    ("PALABRA",      r"[A-Za-z_][A-Za-z0-9_]*"),
    ("T_RELOP",      r">=|<=|==|!=|=|>|<"),
    ("T_PUNTO",      r"\."),
    ("T_PARI",       r"\("),
    ("T_PARD",       r"\)"),
    ("T_ERROR",      r"."),
]
_MAESTRO = re.compile("|".join(f"(?P<{nombre}>{patron})" for nombre, patron in _PATRONES))


@dataclass
class Token:
    lexema: str
    token: str
    categoria: str
    linea: int
    columna: int

    def to_dict(self):
        return asdict(self)


def analizar(texto: str):
    """Devuelve (tokens, errores) para el texto de entrada."""
    tokens, errores = [], []
    linea, inicio_linea = 1, 0

    for m in _MAESTRO.finditer(texto):
        tipo, lexema = m.lastgroup, m.group()
        columna = m.start() - inicio_linea + 1

        if tipo == "SALTO":
            linea += 1
            inicio_linea = m.end()
            continue
        if tipo in ("ESPACIO", "COMENTARIO"):
            continue
        if tipo == "PALABRA":
            tipo = PALABRAS_RESERVADAS.get(lexema, "T_ID")

        tok = Token(lexema, tipo, CATEGORIA[tipo], linea, columna)
        tokens.append(tok)
        if tipo == "T_ERROR":
            errores.append(
                f"Línea {linea}, columna {columna}: el carácter «{lexema}» no pertenece al alfabeto del lenguaje."
            )

    return tokens, errores


def resaltar(texto: str):
    """Divide el texto en líneas de fragmentos (texto, categoría) para pintarlo en la interfaz."""
    lineas = [[]]
    for m in _MAESTRO.finditer(texto):
        tipo, lexema = m.lastgroup, m.group()
        if tipo == "SALTO":
            lineas.append([])
        elif tipo == "ESPACIO":
            lineas[-1].append((lexema, None))
        elif tipo == "COMENTARIO":
            lineas[-1].append((lexema, "comentario"))
        else:
            if tipo == "PALABRA":
                tipo = PALABRAS_RESERVADAS.get(lexema, "T_ID")
            lineas[-1].append((lexema, CATEGORIA[tipo]))
    return lineas


def resumen(tokens):
    """Agrupa los lexemas distintos reconocidos por cada token."""
    agrupado = {}
    for t in tokens:
        entrada = agrupado.setdefault(t.token, {"categoria": t.categoria, "lexemas": [], "total": 0})
        entrada["total"] += 1
        if t.lexema not in entrada["lexemas"]:
            entrada["lexemas"].append(t.lexema)
    orden = [token for token, *_ in CATALOGO] + ["T_ERROR"]
    return [(tok, agrupado[tok]) for tok in orden if tok in agrupado]
