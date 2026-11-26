"""Integración: API de la aplicación Flask."""
import io

import pytest

from app import app


@pytest.fixture()
def cliente():
    app.config["TESTING"] = True
    return app.test_client()


def test_interfaz(cliente):
    r = cliente.get("/")
    assert r.status_code == 200 and b"Compilador" in r.data
    assert cliente.get("/hola").status_code == 200
    assert cliente.get("/ejemplos/reglas_validas.dsl").status_code == 200


def test_compilar_json(cliente):
    r = cliente.post("/api/compilar", json={"codigo": "SI COMPRA.total > 5 ENTONCES APLICAR DESCUENTO(5%)"})
    datos = r.get_json()
    assert r.status_code == 200 and datos["aceptado"]
    assert datos["semantico"]["objeto_json"]["listo_para_activar"]


def test_compilar_archivo(cliente):
    archivo = (io.BytesIO("SI CLIENTE.nivel = VIP ENTONCES APLICAR DESCUENTO(15%)".encode()), "reglas.dsl")
    r = cliente.post("/api/compilar", data={"archivo": archivo}, content_type="multipart/form-data")
    assert r.get_json()["aceptado"]


def test_archivo_con_extension_invalida(cliente):
    archivo = (io.BytesIO(b"SI"), "reglas.pdf")
    r = cliente.post("/api/compilar", data={"archivo": archivo}, content_type="multipart/form-data")
    assert r.status_code == 400


def test_tokens_y_automatas(cliente):
    assert len(cliente.post("/api/tokens", json={"codigo": "SI NO"}).get_json()["tokens"]) == 2
    datos = cliente.get("/api/automatas").get_json()
    assert len(datos["tokens"]) == 17
    assert cliente.get("/api/catalogo").get_json()["dominio"]["objetos"]["CLIENTE"]
