# DSL de Reglas de Descuento — Etapa 1

Trabajo final de **Compiladores** · USIL 2026-2 · Docente: Delgado Enríquez, Héctor Odín

Integrantes: Hernández Aguilar, Diego Patricio · Buitrón Pomasongo, Adrián Samir · Valdez Boza, Diego Manuel · Gutierrez Mamani, Joseph Michael

## Qué incluye la Etapa 1

| Paso | Requisito | Archivo |
|---|---|---|
| 1 | GUI inicial: `index.html` con un "Hola Mundo", para subir a GitHub y publicar | `index.html` + `static/` |
| 2 | App Python con Flask: enunciado del proyecto, bloque para **subir un archivo** o **escribir** el lenguaje (con ejemplo ya digitado) y generación de **TOKENS y LEXEMAS** | `app.py`, `lexer.py`, `templates/index.html` |
| 3 | Publicación en un hosting gratuito (Render) | `render.yaml`, `requirements.txt` |

```
Etapa1/
├── index.html              ← Hola Mundo (GitHub Pages)
├── app.py                  ← Aplicación Flask
├── lexer.py                ← Analizador léxico (tokens y lexemas)
├── templates/index.html    ← Interfaz de la app Flask
├── static/estilos.css      ← Estilos compartidos por ambas páginas
├── static/icono.svg
├── ejemplos/
│   ├── reglas_ejemplo.dsl      ← reglas válidas (también precargadas en el editor)
│   └── reglas_con_errores.dsl  ← para probar los errores léxicos
├── requirements.txt
└── render.yaml             ← Configuración de despliegue en Render
```

## Ejecutar en local

```bash
cd Etapa1
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abrir http://127.0.0.1:5000

## Cómo funciona el analizador léxico

`lexer.py` recorre la entrada de izquierda a derecha aplicando la **coincidencia más larga**:

- Las palabras se reconocen primero con la ER de identificador `(L|_)(L|D|_)*` y luego se buscan en la tabla de palabras reservadas (`SI`, `SINO`, `ENTONCES`, `APLICAR`, `DESCUENTO`, `Y`, `O`, `NO`, `CLIENTE`, `COMPRA`, `TIEMPO`).
- `T_PORCENTAJE` (`D+%`) se prueba antes que `T_NUM` (`D+`), y los operadores de dos caracteres (`>=`, `<=`, `==`, `!=`) antes que los de uno.
- Se ignoran los espacios, los saltos de línea y los comentarios `// ...`.
- Cualquier carácter fuera del alfabeto produce `T_ERROR`, con su línea y columna.

| Token | Expresión regular | Ejemplo |
|---|---|---|
| T_SI, T_SINO, T_ENTONCES, T_APLICAR, T_DESCUENTO, T_TIEMPO | la propia palabra | `SI` |
| T_AND, T_OR, T_NOT | `Y`, `O`, `NO` | `Y` |
| T_OBJETO | `(CLIENTE\|COMPRA)` | `CLIENTE` |
| T_ID | `(L\|_)(L\|D\|_)*` | `nivel`, `VIP` |
| T_NUM | `D+` | `500` |
| T_PORCENTAJE | `D+%` | `15%` |
| T_RELOP | `= \| == \| != \| >(=)? \| <(=)?` | `>=` |
| T_PUNTO, T_PARI, T_PARD | `\.`, `\(`, `\)` | `.` `(` `)` |

También hay un endpoint JSON: `POST /api/tokens` con `{"codigo": "SI COMPRA.total > 500 ..."}`.

## Subir a GitHub

```bash
cd Etapa1
git init
git add .
git commit -m "Etapa 1: GUI inicial y analizador léxico"
git branch -M main
git remote add origin https://github.com/<usuario>/dsl-descuentos.git
git push -u origin main
```

### Publicar el `index.html` (Hola Mundo) en GitHub Pages

En el repositorio: **Settings → Pages → Source: Deploy from a branch → `main` / `(root)`**. Quedará en `https://<usuario>.github.io/dsl-descuentos/`.

## Publicar la app Flask en Render (gratis)

1. Entrar a https://render.com con la cuenta de GitHub.
2. **New → Blueprint** y elegir el repositorio. Render lee `render.yaml` y crea el servicio `dsl-descuentos` en el plan gratuito.
   - O bien **New → Web Service**, con *Build command* `pip install -r requirements.txt` y *Start command* `gunicorn app:app`.
   - Si se sube la carpeta `Entregable2` completa en lugar de `Etapa1`, hay que poner **Root Directory = `Etapa1`**.
3. Cuando termine el despliegue, copiar la URL (por ejemplo `https://dsl-descuentos.onrender.com`) y pegarla en el botón "Abrir el analizador léxico" de `index.html`.

> En el plan gratuito, Render apaga el servicio tras 15 minutos sin uso; la primera visita después de eso tarda unos 30–50 segundos en responder.
