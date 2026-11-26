"""Etapa 3: analizador sintáctico generado con ANTLR, árbol y derivaciones."""
import compilador
from lexer import analizar as lexico
from sintactico import analizar


def test_cadenas_aceptadas(cadenas):
    for cadena in cadenas["aceptadas"]:
        r = analizar(cadena)
        assert r["ok"], (cadena, r["errores"])


def test_cadenas_rechazadas_en_la_fase_correcta(cadenas):
    for caso in cadenas["rechazadas"]:
        r = compilador.compilar(caso["cadena"])
        assert r["fase_con_error"] == caso["fase"], caso


def test_error_sintactico_con_linea_y_columna():
    r = analizar("SI COMPRA.total > 500\nAPLICAR DESCUENTO(10%)")
    assert not r["ok"]
    e = r["errores"][0]
    assert (e["linea"], e["columna"]) == (2, 1)
    assert "ENTONCES" in e["mensaje"]


def test_derivaciones_terminan_en_la_cadena():
    texto = "SI CLIENTE.nivel = VIP Y COMPRA.total > 500 Y TIEMPO(enrango) ENTONCES APLICAR DESCUENTO(15%)"
    r = analizar(texto)
    lexemas = " ".join(t.lexema for t in lexico(texto)[0])
    regla = r["reglas"][0]
    for clave in ("derivacion_izquierda", "derivacion_derecha"):
        pasos = regla[clave]
        assert pasos[0]["forma"] == "REGLA"
        assert pasos[-1]["forma"] == lexemas
        assert len(pasos) == len(regla["derivacion_izquierda"])


def test_derivacion_izquierda_como_el_informe():
    r = analizar("SI CLIENTE.nivel = VIP ENTONCES APLICAR DESCUENTO(15%)")
    pasos = r["reglas"][0]["derivacion_izquierda"]
    assert pasos[1]["produccion"] == "REGLA → T_SI CONDICION T_ENTONCES ACCION RESTO"
    assert pasos[-1]["produccion"] == "RESTO → ε"


def test_varias_reglas_y_sino():
    texto = ("SI CLIENTE.nivel = VIP ENTONCES APLICAR DESCUENTO(15%) SINO SI COMPRA.total > 500 "
             "ENTONCES APLICAR DESCUENTO(10%) SINO APLICAR DESCUENTO(0%)\nSI TIEMPO(navidad) ENTONCES APLICAR DESCUENTO(5%)")
    r = compilador.compilar(texto)
    assert r["sintactico"]["ok"]
    assert [x["id"] for x in r["sintactico"]["reglas"]] == ["R1", "R2"]
    ramas = r["semantico"]["objeto_json"]["reglas"][0]["ramas"]
    assert [x["tipo"] for x in ramas] == ["SI", "SINO SI", "SINO"]
    assert [x["descuento"] for x in ramas] == [15, 10, 0]


def test_precedencia_no_y_o():
    """NO > Y > O: 'NO a Y b O c' se agrupa como ((NO a) Y b) O c."""
    r = compilador.compilar("SI NO TIEMPO(navidad) Y COMPRA.total > 5 O CLIENTE.nivel = VIP ENTONCES APLICAR DESCUENTO(5%)")
    cond = r["semantico"]["objeto_json"]["reglas"][0]["ramas"][0]["condicion"]
    assert cond["tipo"] == "O"
    assert cond["operandos"][0]["tipo"] == "Y"
    assert cond["operandos"][0]["operandos"][0]["tipo"] == "NO"


def test_arbol_dot():
    r = analizar("SI COMPRA.total > 5 ENTONCES APLICAR DESCUENTO(5%)")
    assert r["arbol_programa_dot"].startswith("digraph")
    assert "PROGRAMA" in r["arbol_programa_dot"] and "ε" in r["reglas"][0]["arbol_dot"]
