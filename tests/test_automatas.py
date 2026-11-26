"""Etapa 2: ER → AFND (Thompson) → AFD (subconjuntos) → AFD mínimo."""
import itertools
import random
import re

import pytest

from automatas import EPSILON, acepta, automatas_de_tokens, construir_token, thompson, subconjuntos
from lexer import CATALOGO, _PATRONES

PATRON = dict(_PATRONES)
PATRON_TOKEN = {
    "T_ID": PATRON["PALABRA"], "T_NUM": PATRON["T_NUM"], "T_PORCENTAJE": PATRON["T_PORCENTAJE"],
    "T_RELOP": PATRON["T_RELOP"], "T_PUNTO": r"\.", "T_PARI": r"\(", "T_PARD": r"\)",
    "T_OBJETO": "CLIENTE|COMPRA",
}
ALFABETO_PRUEBA = "SINOEACLMPRTUDYVX_aeiz0159%=<>!.()"


def _patron(token, er):
    return PATRON_TOKEN.get(token, re.escape(er))


def _cadenas(n=4000, semilla=7):
    rnd = random.Random(semilla)
    fijas = [e.strip() for _, _, ejemplos, _ in CATALOGO for e in ejemplos.split(",")]
    aleatorias = ["".join(rnd.choice(ALFABETO_PRUEBA) for _ in range(rnd.randint(1, 9))) for _ in range(n)]
    return fijas + aleatorias


@pytest.mark.parametrize("token,categoria,ejemplos,er", CATALOGO, ids=[c[0] for c in CATALOGO])
def test_afd_equivale_a_la_expresion_regular(token, categoria, ejemplos, er):
    afnd, afd, minimo, clases = construir_token(token, er)
    regex = re.compile(_patron(token, er))
    for cadena in _cadenas():
        esperado = regex.fullmatch(cadena) is not None
        assert acepta(afd, cadena, clases) == esperado, (token, cadena)
        assert acepta(minimo, cadena, clases) == esperado, (token, cadena)


@pytest.mark.parametrize("token,categoria,ejemplos,er", CATALOGO, ids=[c[0] for c in CATALOGO])
def test_minimo_no_tiene_mas_estados(token, categoria, ejemplos, er):
    afnd, afd, minimo, _ = construir_token(token, er)
    assert len(minimo.estados) <= len(afd.estados)
    assert len(afd.finales) >= 1 and len(minimo.finales) >= 1


def test_palabra_reservada_sin_epsilon():
    """Como en el informe: el AFND de SI es la cadena q0 -S-> q1 -I-> q2."""
    a = thompson("SI")
    assert a.estados == ["q0", "q1", "q2"]
    assert a.transiciones == {("q0", "S"): {"q1"}, ("q1", "I"): {"q2"}}
    assert a.finales == {"q2"}


def test_afnd_de_union_usa_epsilon():
    a = thompson("(CLIENTE|COMPRA)")
    assert any(s == EPSILON for (_, s) in a.transiciones)
    assert all(s != EPSILON for (_, s) in subconjuntos(a).transiciones)


def test_t_id_minimo_tiene_dos_estados():
    _, _, minimo, _ = construir_token("T_ID", "(L|_)(L|D|_)*")
    assert len(minimo.estados) == 2


def test_serializacion_completa():
    datos = automatas_de_tokens()
    assert len(datos) == len(CATALOGO)
    for t in datos:
        for vista in ("afnd", "afd", "minimo"):
            a = t[vista]
            assert set(a["quintupla"]) == {"Q", "Σ", "δ", "q0", "F"}
            assert a["dot"].startswith("digraph")
            assert len(a["tabla"]["filas"]) == a["estados"]
