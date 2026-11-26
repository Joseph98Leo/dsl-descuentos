"""Etapa 1: analizador léxico (lexer.py) y su coincidencia con el lexer generado por ANTLR."""
import pytest

from lexer import analizar
from sintactico import tokens_antlr


def test_ejemplo_sin_errores(ejemplos):
    tokens, errores = analizar(ejemplos["reglas_ejemplo.dsl"])
    assert errores == []
    assert len(tokens) == 75


def test_coincidencia_mas_larga():
    tokens, _ = analizar("COMPRA.total >= 15% SINO SI x_1")
    assert [(t.token, t.lexema) for t in tokens] == [
        ("T_OBJETO", "COMPRA"), ("T_PUNTO", "."), ("T_ID", "total"), ("T_RELOP", ">="),
        ("T_PORCENTAJE", "15%"), ("T_SINO", "SINO"), ("T_SI", "SI"), ("T_ID", "x_1"),
    ]


def test_posiciones_y_comentarios():
    tokens, _ = analizar("// comentario\n  SI  NO")
    assert [(t.lexema, t.linea, t.columna) for t in tokens] == [("SI", 2, 3), ("NO", 2, 7)]


@pytest.mark.parametrize("caracter", ["&", "$", ";", "#", "@"])
def test_caracter_fuera_del_alfabeto(caracter):
    tokens, errores = analizar(f"SI COMPRA.total > 5{caracter}")
    assert len(errores) == 1 and caracter in errores[0]
    assert tokens[-1].token == "T_ERROR"


def test_lexer_manual_y_antlr_coinciden(ejemplos, cadenas):
    textos = [ejemplos["reglas_ejemplo.dsl"], ejemplos["reglas_validas.dsl"]] + cadenas["aceptadas"]
    for texto in textos:
        manual = [(t.token, t.lexema) for t in analizar(texto)[0]]
        assert manual == tokens_antlr(texto), texto
