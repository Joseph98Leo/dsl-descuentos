# Compilador DSL de Reglas de Descuento

Trabajo final de **Compiladores** · USIL 2026-2 · Docente: Delgado Enríquez, Héctor Odín

Integrantes: Hernández Aguilar, Diego Patricio · Buitrón Pomasongo, Adrián Samir · Valdez Boza, Diego Manuel · Gutierrez Mamani, Joseph Michael

Un lenguaje de dominio específico (DSL) para que el área comercial escriba reglas de descuento, y su compilador, que las valida antes de activarlas:

```
SI CLIENTE.nivel = VIP Y COMPRA.total > 500 ENTONCES APLICAR DESCUENTO(15%)
SINO SI CLIENTE.nivel = VIP ENTONCES APLICAR DESCUENTO(10%)
SINO APLICAR DESCUENTO(0%)
```

```
texto ─► 1. léxico ─► 3. sintáctico (ANTLR) ─► 4. semántico ─► objeto JSON
            │
            └► 2. autómatas de cada token (ER → AFND → AFD → AFD mínimo)
```

## Etapas del proyecto

| Etapa | Qué pide el curso | Dónde está |
|---|---|---|
| **1** | GUI inicial ("Hola Mundo"), app Flask con el enunciado, subir o escribir el lenguaje, **tokens y lexemas**, publicación en hosting | `index.html`, `app.py`, `lexer.py`, `analizador.html` |
| **2** | Para cada token: **ER, AFND, AFD, tabla de transiciones, quíntupla y gráfico generado desde el código** (no imagen) | `automatas.py` |
| **3** | **Gramática**, **árbol** y **metacompilador** (lexer y parser generados) | `gramatica/ReglasDescuento.g4` → ANTLR 4.13.2 → `generado/`; `sintactico.py` |
| **4** | **Integración**, **análisis semántico**, **pruebas**, **resultados** e **impresión en PDF** | `semantico.py`, `compilador.py`, `tests/`, `evaluar.py`, `resultados/`, botón "Imprimir / guardar PDF" |

### Qué hace cada fase

- **Léxico** (`lexer.py`): coincidencia más larga, palabras reservadas, comentarios `//`, línea y columna de cada token y de cada carácter fuera del alfabeto. Una prueba comprueba que da exactamente los mismos tokens que el lexer generado por ANTLR.
- **Autómatas** (`automatas.py`): analiza la ER de cada token del catálogo y construye el AFND por el método de Thompson, el AFD por el método de subconjuntos (indicando qué estados del AFND forma cada estado del AFD) y el AFD mínimo por partición de estados. Genera la quíntupla, la tabla de transiciones y el gráfico en lenguaje DOT, que el navegador dibuja con viz.js. En la página se puede probar una cadena y ver el recorrido por los estados.
- **Sintáctico** (`sintactico.py`): usa el analizador que ANTLR genera desde la GLC del informe. Reporta los errores en español con línea y columna, y construye para cada regla el **árbol de derivación** y las **derivaciones por la izquierda y por la derecha**, paso a paso con la producción aplicada.
- **Semántico** (`semantico.py`, `dominio.json`): consulta la tabla de símbolos del dominio y detecta:
  - atributos inexistentes, tipos incompatibles, valores no permitidos, operadores inválidos para atributos categóricos, periodos de `TIEMPO(…)` desconocidos y descuentos fuera de 0–100 %;
  - **contradicciones** (una condición que nunca se cumple) y **ramas inalcanzables** (un `SINO SI` que ya cubren las ramas anteriores);
  - **colisiones**: dos reglas que pueden aplicarse a la misma compra y acumular descuentos, con un ejemplo concreto de transacción. La detección es exacta: cada condición se lleva a forma normal disyuntiva y se resuelve sobre intervalos (numéricos) y conjuntos (categóricos).
- **JSON**: un objeto por regla con su estado (`aceptada`, `en_colision` o `rechazada`), sus ramas, sus condiciones y su descuento, listo para un motor de reglas. Se puede descargar desde la página.

## Resultados

`python evaluar.py` mide los objetivos específicos y guarda el detalle en `resultados/metricas.md`:

| Objetivo | Meta | Resultado |
|---|---|---|
| OE1 · Tokens modelados (ER, AFND, AFD, quíntupla) | ≥ 15 | 17 |
| OE2 · Cadenas de prueba clasificadas correctamente | ≥ 5 | 34 de 34 (100 %) |
| OE3 · Solapamientos configurados detectados | ≥ 90 % | 13 de 13 (100 %), 0 falsos positivos |
| OE4 · Objetos JSON generados | uno por regla | 13 |
| OE5 · Pruebas automatizadas exitosas | > 95 % | 80 de 80 (100 %) |
| RNF · Tiempo de análisis por regla | < 200 ms | ~0,3 ms en promedio |

Los casos de prueba están en `casos/cadenas.json` y `casos/colisiones.json`.

## Ejecutar en local

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python app.py                      # http://127.0.0.1:5000
```

Otras órdenes:

```bash
pytest                                     # pruebas automatizadas (80)
python evaluar.py                          # métricas → resultados/metricas.md
python compilador.py ejemplos/reglas_ejemplo.dsl   # compilar desde la terminal
python automatas.py                        # resumen de estados de cada autómata
bash herramientas/generar_parser.sh        # regenerar el parser con ANTLR (requiere Java)
```

El analizador generado ya está en `generado/`, así que para ejecutar la app **no hace falta Java**: solo para volver a generarlo si se cambia la gramática.

## API

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/compilar` | `{"codigo": "..."}` o un archivo `.dsl/.txt/.reglas` en el campo `archivo`. Devuelve todas las fases. |
| `POST` | `/api/tokens` | Solo el análisis léxico. |
| `GET` | `/api/automatas` | ER, AFND, AFD y AFD mínimo de cada token. |
| `GET` | `/api/catalogo` | Catálogo de tokens y tabla de símbolos del dominio. |

## Publicación

- **GitHub Pages** (sin servidor): `index.html` es el "Hola Mundo" y `analizador.html` el compilador. Como Pages no ejecuta Flask, la página carga **Pyodide** (Python en WebAssembly), instala el runtime de ANTLR y ejecuta en el navegador **los mismos módulos `.py`**. Si encuentra la API de Flask, la usa en su lugar.
- **Render** (app Flask): `render.yaml` ya está configurado (`gunicorn app:app`).

## Estructura

```
├── index.html                 Hola Mundo (Etapa 1)
├── analizador.html            Interfaz del compilador (Flask y GitHub Pages)
├── app.py                     Aplicación Flask y API
├── lexer.py                   Etapa 1 · analizador léxico
├── automatas.py               Etapa 2 · ER → AFND → AFD → AFD mínimo
├── gramatica/ReglasDescuento.g4   Etapa 3 · GLC para ANTLR
├── generado/                  Etapa 3 · lexer y parser generados por ANTLR
├── sintactico.py              Etapa 3 · errores, árbol, derivaciones, AST
├── semantico.py               Etapa 4 · validaciones, colisiones, JSON
├── dominio.json               Tabla de símbolos del dominio
├── compilador.py              Integración de todas las fases
├── evaluar.py                 Métricas de los objetivos
├── casos/                     Cadenas de prueba y colisiones configuradas
├── ejemplos/                  Archivos .dsl de ejemplo (válidos y con errores)
├── tests/                     Pruebas automatizadas (pytest)
├── resultados/                Métricas generadas
├── herramientas/generar_parser.sh
├── static/                    estilos.css, app.js, icono.svg
├── requirements.txt / requirements-dev.txt
└── render.yaml
```
