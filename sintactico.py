"""
Etapa 3 — Análisis sintáctico con el analizador generado por ANTLR.

El analizador léxico y sintáctico de la carpeta generado/ lo produce el
metacompilador ANTLR a partir de gramatica/ReglasDescuento.g4 (la GLC del
informe). Este módulo:

  - ejecuta el analizador y traduce sus errores al español, con línea y columna;
  - convierte el árbol de ANTLR en el árbol de derivación del informe
    (PROGRAMA, REGLA, CONDICION, …), con ε donde RESTO no deriva nada;
  - genera las derivaciones por la izquierda y por la derecha de cada regla;
  - dibuja el árbol en lenguaje DOT;
  - construye el árbol de sintaxis abstracta (AST) que usa el análisis semántico.
"""

from __future__ import annotations

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener
from antlr4.tree.Tree import ErrorNode, TerminalNode

from generado.ReglasDescuentoLexer import ReglasDescuentoLexer
from generado.ReglasDescuentoParser import ReglasDescuentoParser

EPSILON = "ε"

# Cómo se nombra cada token en los mensajes de error.
DESCRIPCION_TOKEN = {
    "T_SI": "SI", "T_SINO": "SINO", "T_ENTONCES": "ENTONCES", "T_APLICAR": "APLICAR",
    "T_DESCUENTO": "DESCUENTO", "T_AND": "Y", "T_OR": "O", "T_NOT": "NO",
    "T_OBJETO": "CLIENTE o COMPRA", "T_TIEMPO": "TIEMPO", "T_ID": "un identificador",
    "T_NUM": "un número", "T_PORCENTAJE": "un porcentaje (ej. 15%)",
    "T_RELOP": "un operador relacional (=, ==, !=, >, >=, <, <=)",
    "T_PUNTO": "«.»", "T_PARI": "«(»", "T_PARD": "«)»", "EOF": "el fin del archivo",
}


# =============================================================================
# Errores
# =============================================================================

class _Recolector(ErrorListener):
    def __init__(self, tipo):
        self.tipo = tipo
        self.errores = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        if self.tipo == "léxico":
            caracter = msg.split("at: ", 1)[-1].strip("'") if "at: " in msg else "?"
            texto = f"el carácter «{caracter}» no pertenece al alfabeto del lenguaje."
        else:
            encontrado = "el fin del archivo" if offendingSymbol.type == -1 else f"«{offendingSymbol.text}»"
            esperados = _esperados(recognizer)
            if "missing" in msg:
                texto = f"falta {esperados} antes de {encontrado}."
            elif "extraneous" in msg:
                texto = f"sobra {encontrado}; se esperaba {esperados}."
            else:
                texto = f"se encontró {encontrado} pero se esperaba {esperados}."
        self.errores.append({
            "tipo": self.tipo,
            "linea": line,
            "columna": column + 1,
            "mensaje": f"Línea {line}, columna {column + 1}: {texto}",
        })


def _esperados(parser) -> str:
    try:
        conjunto = parser.getExpectedTokens()
    except Exception:
        return "otra cosa"
    nombres = []
    for intervalo in conjunto.intervals or []:
        for t in intervalo:
            simbolo = "EOF" if t == -1 else parser.symbolicNames[t]
            nombres.append(DESCRIPCION_TOKEN.get(simbolo, simbolo))
    if not nombres:
        return "otra cosa"
    return nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " o " + nombres[-1]


# =============================================================================
# Árbol de derivación
# =============================================================================

def _nombre_regla(ctx) -> str:
    return ReglasDescuentoParser.ruleNames[ctx.getRuleIndex()].upper()


def _arbol(ctx, contador):
    """Árbol de ANTLR → diccionario {id, nombre, tipo, lexema, hijos}."""
    nodo_id = contador[0]
    contador[0] += 1
    if isinstance(ctx, TerminalNode):
        simbolo = ctx.getSymbol()
        return {"id": nodo_id, "nombre": ReglasDescuentoParser.symbolicNames[simbolo.type],
                "tipo": "terminal", "lexema": simbolo.text, "hijos": []}
    nodo = {"id": nodo_id, "nombre": _nombre_regla(ctx), "tipo": "noterminal", "lexema": None, "hijos": []}
    hijos = list(ctx.getChildren()) if ctx.getChildCount() else []
    if not hijos:  # RESTO → ε
        nodo["hijos"].append({"id": contador[0], "nombre": EPSILON, "tipo": "epsilon", "lexema": None, "hijos": []})
        contador[0] += 1
    for h in hijos:
        nodo["hijos"].append(_arbol(h, contador))
    return nodo


def _simbolo(nodo) -> str:
    return nodo["lexema"] if nodo["tipo"] == "terminal" else nodo["nombre"]


def _produccion(nodo) -> str:
    derecha = " ".join(EPSILON if h["tipo"] == "epsilon" else h["nombre"] for h in nodo["hijos"])
    return f"{nodo['nombre']} → {derecha}"


def derivacion(raiz, por="izquierda"):
    """Pasos de la derivación más a la izquierda (o a la derecha) que produce el árbol.
    Cada paso indica la producción aplicada y la forma sentencial resultante."""
    forma = [raiz]
    pasos = [{"produccion": None, "forma": raiz["nombre"]}]
    while True:
        indices = [i for i, n in enumerate(forma) if n["tipo"] == "noterminal"]
        if not indices:
            break
        i = indices[0] if por == "izquierda" else indices[-1]
        nodo = forma[i]
        hijos = [h for h in nodo["hijos"] if h["tipo"] != "epsilon"]
        forma = forma[:i] + hijos + forma[i + 1:]
        pasos.append({
            "produccion": _produccion(nodo),
            "forma": " ".join(_simbolo(n) for n in forma) or EPSILON,
        })
    return pasos


def _escapar(texto: str) -> str:
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def arbol_dot(raiz) -> str:
    """Árbol de derivación en lenguaje DOT."""
    lineas = [
        "digraph arbol {",
        '  bgcolor="transparent"; pad=0.2; nodesep=0.18; ranksep=0.32;',
        '  node [shape=plaintext, fontname="IBM Plex Mono", fontsize=11, fontcolor="#2b241d"];',
        '  edge [color="#a1958a", arrowhead=none];',
    ]

    def visitar(n):
        if n["tipo"] == "noterminal":
            etiqueta = f'<<B>{_escapar(n["nombre"])}</B>>'
        elif n["tipo"] == "epsilon":
            etiqueta = '<<FONT COLOR="#8a7f74">ε</FONT>>'
        else:
            etiqueta = (f'<<FONT POINT-SIZE="9" COLOR="#7a6e62">{_escapar(n["nombre"])}</FONT>'
                        f'<BR/><FONT COLOR="#8a3b1c">{_escapar(n["lexema"])}</FONT>>')
        lineas.append(f'  n{n["id"]} [label={etiqueta}];')
        for h in n["hijos"]:
            visitar(h)
            lineas.append(f'  n{n["id"]} -> n{h["id"]};')

    visitar(raiz)
    lineas.append("}")
    return "\n".join(lineas)


# =============================================================================
# Árbol de sintaxis abstracta (para el análisis semántico)
# =============================================================================

P = ReglasDescuentoParser


def _pos(token):
    return {"linea": token.line, "columna": token.column + 1}


def _condicion(ctx):
    if isinstance(ctx, P.CondicionContext):
        if ctx.T_OR():
            izq, der = _condicion(ctx.condicion()), _condicion(ctx.termino())
            return {"tipo": "O", "operandos": _aplanar("O", izq) + _aplanar("O", der)}
        return _condicion(ctx.termino())
    if isinstance(ctx, P.TerminoContext):
        if ctx.T_AND():
            izq, der = _condicion(ctx.termino()), _condicion(ctx.factor())
            return {"tipo": "Y", "operandos": _aplanar("Y", izq) + _aplanar("Y", der)}
        return _condicion(ctx.factor())
    if isinstance(ctx, P.FactorContext):
        if ctx.T_NOT():
            return {"tipo": "NO", "operando": _condicion(ctx.factor()), **_pos(ctx.T_NOT().getSymbol())}
        if ctx.T_PARI():
            return _condicion(ctx.condicion())
        if ctx.comparacion():
            c = ctx.comparacion()
            attr, op = c.atributo(), c.operando()
            valor_tok = op.getChild(0).getSymbol()
            return {
                "tipo": "comparacion",
                "objeto": attr.T_OBJETO().getText(),
                "atributo": attr.T_ID().getText(),
                "operador": c.T_RELOP().getText(),
                "valor": {"token": P.symbolicNames[valor_tok.type], "texto": valor_tok.text, **_pos(valor_tok)},
                **_pos(attr.T_OBJETO().getSymbol()),
            }
        f = ctx.funcion_tiempo()
        return {"tipo": "tiempo", "periodo": f.T_ID().getText(), **_pos(f.T_ID().getSymbol())}
    raise ValueError(f"Nodo inesperado: {type(ctx).__name__}")


def _aplanar(tipo, nodo):
    return nodo["operandos"] if nodo["tipo"] == tipo else [nodo]


def _accion(ctx):
    tok = ctx.T_PORCENTAJE().getSymbol()
    return {"texto": tok.text, "valor": int(tok.text[:-1]), **_pos(tok)}


def _ast_regla(ctx, numero, texto_fuente):
    ramas = [{"tipo": "SI", "condicion": _condicion(ctx.condicion()), "descuento": _accion(ctx.accion()),
              **_pos(ctx.T_SI().getSymbol())}]
    resto = ctx.resto()
    while resto is not None and resto.getChildCount():
        if resto.T_SI():
            ramas.append({"tipo": "SINO SI", "condicion": _condicion(resto.condicion()),
                          "descuento": _accion(resto.accion()), **_pos(resto.T_SINO().getSymbol())})
            resto = resto.resto()
        else:
            ramas.append({"tipo": "SINO", "condicion": None, "descuento": _accion(resto.accion()),
                          **_pos(resto.T_SINO().getSymbol())})
            resto = None
    inicio, fin = ctx.start.start, ctx.stop.stop
    return {
        "id": f"R{numero}",
        "linea": ctx.start.line,
        "texto": " ".join(texto_fuente[inicio:fin + 1].split()),
        "ramas": ramas,
    }


# =============================================================================
# Punto de entrada
# =============================================================================

def analizar(texto: str) -> dict:
    """Analiza el programa completo. Devuelve los errores o, si no hay, el árbol,
    las derivaciones de cada regla y el AST."""
    lexer = ReglasDescuentoLexer(InputStream(texto))
    errores_lexicos = _Recolector("léxico")
    lexer.removeErrorListeners()
    lexer.addErrorListener(errores_lexicos)

    tokens = CommonTokenStream(lexer)
    parser = ReglasDescuentoParser(tokens)
    errores_sintacticos = _Recolector("sintáctico")
    parser.removeErrorListeners()
    parser.addErrorListener(errores_sintacticos)

    arbol_antlr = parser.inicio()
    errores = errores_lexicos.errores + errores_sintacticos.errores
    if errores:
        return {"ok": False, "errores": errores, "reglas": [], "ast": []}

    # Árbol completo desde PROGRAMA (se omite el símbolo auxiliar INICIO y el EOF).
    programa_ctx = arbol_antlr.programa()
    raiz = _arbol(programa_ctx, [0])

    reglas, ast = [], []
    ctx, numero = programa_ctx, 1
    while ctx is not None:
        regla_ctx = ctx.regla()
        nodo = _arbol(regla_ctx, [0])
        regla_ast = _ast_regla(regla_ctx, numero, texto)
        ast.append(regla_ast)
        reglas.append({
            "id": regla_ast["id"],
            "linea": regla_ast["linea"],
            "texto": regla_ast["texto"],
            "arbol_dot": arbol_dot(nodo),
            "derivacion_izquierda": derivacion(nodo, "izquierda"),
            "derivacion_derecha": derivacion(nodo, "derecha"),
        })
        ctx, numero = ctx.programa(), numero + 1

    return {
        "ok": True,
        "errores": [],
        "arbol_programa_dot": arbol_dot(raiz),
        "nodos_programa": _contar(raiz),
        "reglas": reglas,
        "ast": ast,
    }


def _contar(nodo) -> int:
    return 1 + sum(_contar(h) for h in nodo["hijos"])


def tokens_antlr(texto: str):
    """Secuencia (token, lexema) del analizador léxico generado por ANTLR.
    Se usa en las pruebas para comprobar que coincide con lexer.py."""
    lexer = ReglasDescuentoLexer(InputStream(texto))
    lexer.removeErrorListeners()
    resultado = []
    for t in lexer.getAllTokens():
        resultado.append((ReglasDescuentoLexer.symbolicNames[t.type], t.text))
    return resultado
