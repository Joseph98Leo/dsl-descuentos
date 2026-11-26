"""Etapa 4: análisis semántico, colisiones (OE3) y objeto JSON (OE4)."""
import json

import pytest

import compilador


def _sem(texto):
    r = compilador.compilar(texto)
    assert r["sintactico"] and r["sintactico"]["ok"], r
    return r["semantico"]


@pytest.mark.parametrize("texto,codigo", [
    ("SI CLIENTE.saldo > 100 ENTONCES APLICAR DESCUENTO(5%)", "ATRIBUTO_DESCONOCIDO"),
    ("SI COMPRA.total = VIP ENTONCES APLICAR DESCUENTO(5%)", "TIPO_INCOMPATIBLE"),
    ("SI COMPRA.total > 10% ENTONCES APLICAR DESCUENTO(5%)", "TIPO_INCOMPATIBLE"),
    ("SI CLIENTE.nivel = 5 ENTONCES APLICAR DESCUENTO(5%)", "TIPO_INCOMPATIBLE"),
    ("SI CLIENTE.nivel = DIAMANTE ENTONCES APLICAR DESCUENTO(5%)", "VALOR_NO_PERMITIDO"),
    ("SI CLIENTE.nivel >= VIP ENTONCES APLICAR DESCUENTO(5%)", "OPERADOR_INVALIDO"),
    ("SI TIEMPO(verano) ENTONCES APLICAR DESCUENTO(5%)", "PERIODO_DESCONOCIDO"),
    ("SI COMPRA.total > 5 ENTONCES APLICAR DESCUENTO(101%)", "DESCUENTO_FUERA_DE_RANGO"),
    ("SI COMPRA.total > 500 Y COMPRA.total < 100 ENTONCES APLICAR DESCUENTO(5%)", "CONTRADICCION"),
    ("SI CLIENTE.nivel = VIP Y CLIENTE.nivel = ORO ENTONCES APLICAR DESCUENTO(5%)", "CONTRADICCION"),
    ("SI TIEMPO(navidad) Y NO TIEMPO(navidad) ENTONCES APLICAR DESCUENTO(5%)", "CONTRADICCION"),
    ("SI COMPRA.cantidad < 1 ENTONCES APLICAR DESCUENTO(5%)", "CONTRADICCION"),
    ("SI CLIENTE.edad > 120 ENTONCES APLICAR DESCUENTO(5%)", "CONTRADICCION"),
])
def test_errores_semanticos(texto, codigo):
    s = _sem(texto)
    assert not s["ok"]
    assert codigo in {e["codigo"] for e in s["errores"]}
    assert s["objeto_json"]["reglas"][0]["estado"] == "rechazada"


def test_rama_inalcanzable():
    s = _sem("SI COMPRA.total > 100 ENTONCES APLICAR DESCUENTO(5%) SINO SI COMPRA.total > 500 ENTONCES APLICAR DESCUENTO(8%)")
    assert s["ok"]
    assert [a["codigo"] for a in s["advertencias"]] == ["RAMA_INALCANZABLE"]


def test_sino_final_inalcanzable():
    s = _sem("SI COMPRA.total >= 0 ENTONCES APLICAR DESCUENTO(5%) SINO APLICAR DESCUENTO(1%)")
    assert [a["codigo"] for a in s["advertencias"]] == ["RAMA_INALCANZABLE"]


def test_reglas_validas_sin_colisiones(ejemplos):
    s = _sem(ejemplos["reglas_validas.dsl"])
    assert s["ok"] and s["colisiones"] == [] and s["advertencias"] == []
    assert s["objeto_json"]["listo_para_activar"]
    assert s["objeto_json"]["resumen"]["aceptadas"] == 3


def test_colisiones_configuradas(casos_colisiones):
    for caso in casos_colisiones:
        s = _sem(caso["reglas"])
        assert s["ok"], (caso["nombre"], s["errores"])
        encontradas = sorted({tuple(c["reglas"]) for c in s["colisiones"]})
        esperadas = sorted(tuple(p) for p in caso["esperadas"])
        assert encontradas == esperadas, caso["nombre"]


def test_ejemplo_de_colision_es_real():
    s = _sem("SI CLIENTE.nivel = VIP ENTONCES APLICAR DESCUENTO(15%)\nSI COMPRA.total > 500 ENTONCES APLICAR DESCUENTO(10%)")
    c = s["colisiones"][0]
    assert c["acumulado"] == 25
    assert "CLIENTE.nivel = VIP" in c["ejemplo"] and "COMPRA.total" in c["ejemplo"]
    assert [r["estado"] for r in s["objeto_json"]["reglas"]] == ["en_colision", "en_colision"]


def test_objeto_json(ejemplos):
    s = _sem(ejemplos["reglas_validas.dsl"])
    obj = json.loads(json.dumps(s["objeto_json"]))
    r1 = obj["reglas"][0]
    assert r1["ramas"][0]["condicion"] == {
        "tipo": "Y", "operandos": [
            {"tipo": "comparacion", "objeto": "CLIENTE", "atributo": "nivel", "operador": "==", "valor": "VIP"},
            {"tipo": "comparacion", "objeto": "COMPRA", "atributo": "total", "operador": ">", "valor": 500},
        ]}
    assert r1["ramas"][2] == {"tipo": "SINO", "condicion": None, "descuento": 0}


def test_rendimiento_menor_a_200_ms(ejemplos):
    """RNF: el análisis de una regla no debe tomar más de 200 ms."""
    for texto in ejemplos.values():
        r = compilador.compilar(texto)
        n = len(r["sintactico"]["reglas"]) if r["sintactico"] and r["sintactico"]["ok"] else 1
        assert r["tiempos_ms"]["total"] / n < 200
