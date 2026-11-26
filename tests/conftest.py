import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))


@pytest.fixture(scope="session")
def cadenas():
    return json.loads((RAIZ / "casos" / "cadenas.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def casos_colisiones():
    return json.loads((RAIZ / "casos" / "colisiones.json").read_text(encoding="utf-8"))["casos"]


@pytest.fixture(scope="session")
def ejemplos():
    return {p.name: p.read_text(encoding="utf-8") for p in (RAIZ / "ejemplos").glob("*.dsl")}
