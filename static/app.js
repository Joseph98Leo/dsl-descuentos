/*
 * Interfaz del compilador DSL de reglas de descuento.
 *
 * Funciona de dos maneras con el mismo código Python:
 *   - Con la app Flask (app.py): llama a la API /api/…
 *   - En GitHub Pages (sin servidor): carga Pyodide (Python en WebAssembly),
 *     instala el runtime de ANTLR y ejecuta los mismos módulos .py en el navegador.
 */
(function () {
  "use strict";

  var EXTENSIONES = [".dsl", ".txt", ".reglas"];
  var CATEGORIAS = ["reservada", "logico", "objeto", "identificador", "literal", "relacional", "delimitador", "error"];
  var EJEMPLOS = [
    { archivo: "reglas_validas.dsl", nombre: "Reglas válidas (sin colisiones)" },
    { archivo: "reglas_ejemplo.dsl", nombre: "Reglas con colisiones" },
    { archivo: "errores_semanticos.dsl", nombre: "Errores semánticos" },
    { archivo: "errores_sintacticos.dsl", nombre: "Errores sintácticos" },
    { archivo: "reglas_con_errores.dsl", nombre: "Errores léxicos" }
  ];
  var ARCHIVOS_PYTHON = [
    "lexer.py", "automatas.py", "sintactico.py", "semantico.py", "compilador.py", "dominio.json",
    "generado/__init__.py", "generado/ReglasDescuentoLexer.py", "generado/ReglasDescuentoParser.py",
    "generado/ReglasDescuentoVisitor.py"
  ];
  var PYODIDE = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js";

  var $ = function (id) { return document.getElementById(id); };
  var form = $("formulario"), codigo = $("codigo"), archivo = $("archivo"), nombre = $("archivo-nombre");
  var boton = $("compilar"), textoBoton = $("texto-boton"), estado = $("estado-motor");
  var motor = null, nombres = {}, ultimo = null;

  // ------------------------------------------------------------------ utilidades

  function el(tag, attrs, contenido) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) if (attrs[k] != null) n.setAttribute(k, attrs[k]);
    if (contenido != null) {
      (Array.isArray(contenido) ? contenido : [contenido]).forEach(function (c) {
        n.appendChild(typeof c === "object" ? c : document.createTextNode(String(c)));
      });
    }
    return n;
  }

  function plural(n, uno, varios) { return n + " " + (n === 1 ? uno : varios); }

  function chip(texto, cat) { return el("span", { "class": "chip k-" + cat }, texto); }

  function vaciar(n) { while (n.firstChild) n.removeChild(n.firstChild); return n; }

  function avisar(mensaje) {
    var a = vaciar($("aviso-entrada"));
    a.hidden = !mensaje;
    if (mensaje) { a.appendChild(el("strong", null, "No se pudo compilar. ")); a.appendChild(document.createTextNode(mensaje)); }
  }

  function tabla(cabeceras, filas, clase) {
    var t = el("table", clase ? { "class": clase } : null);
    var tr = el("tr");
    cabeceras.forEach(function (c) { tr.appendChild(el("th", { scope: "col" }, c)); });
    t.appendChild(el("thead", null, tr));
    var tb = el("tbody");
    filas.forEach(function (f) { tb.appendChild(f); });
    t.appendChild(tb);
    return el("div", { "class": "marco-tabla" }, t);
  }

  // ------------------------------------------------------------------ grafos (viz.js)

  var vizPromesa = null;
  function viz() {
    if (!vizPromesa) {
      vizPromesa = new Promise(function (ok, mal) {
        var intentos = 0;
        (function esperar() {
          if (window.Viz) return ok(window.Viz.instance());
          if (++intentos > 100) return mal(new Error("viz.js no cargó"));
          setTimeout(esperar, 100);
        })();
      });
    }
    return vizPromesa;
  }

  function grafo(dot, etiqueta) {
    var caja = el("figure", { "class": "grafo", role: "img", "aria-label": etiqueta || "Grafo" });
    caja.appendChild(el("span", { "class": "ayuda" }, "Dibujando…"));
    viz().then(function (v) {
      vaciar(caja).appendChild(v.renderSVGElement(dot));
    }).catch(function () {
      vaciar(caja).appendChild(el("pre", { "class": "dot" }, dot));
    });
    return caja;
  }

  // ------------------------------------------------------------------ motor (Flask o Pyodide)

  async function motorServidor() {
    var r = await fetch("api/catalogo");
    if (!r.ok) throw new Error("sin API");
    var catalogo = await r.json();
    return {
      nombre: "Python + Flask (servidor)",
      catalogo: catalogo,
      compilar: async function (texto) {
        var res = await fetch("api/compilar", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ codigo: texto })
        });
        return res.json();
      },
      automatas: async function () { return (await fetch("api/automatas")).json(); }
    };
  }

  function cargarScript(src) {
    return new Promise(function (ok, mal) {
      var s = document.createElement("script");
      s.src = src; s.onload = ok; s.onerror = mal;
      document.head.appendChild(s);
    });
  }

  async function motorNavegador() {
    estado.textContent = "Cargando Python en el navegador (Pyodide)…";
    await cargarScript(PYODIDE);
    var py = await loadPyodide();
    estado.textContent = "Instalando el runtime de ANTLR…";
    await py.loadPackage("micropip");
    await py.pyimport("micropip").install("antlr4-python3-runtime==4.13.2");
    var textos = await Promise.all(ARCHIVOS_PYTHON.map(function (f) {
      return fetch(f).then(function (r) { if (!r.ok) throw new Error(f); return r.text(); });
    }));
    var dir = py.FS.cwd();
    py.FS.mkdirTree(dir + "/generado");
    ARCHIVOS_PYTHON.forEach(function (f, i) { py.FS.writeFile(dir + "/" + f, textos[i]); });
    py.runPython([
      "import json",
      "import compilador, automatas, semantico",
      "from lexer import CATALOGO, NOMBRE_CATEGORIA",
      "def catalogo_json():",
      "    return json.dumps({'catalogo': CATALOGO, 'nombres': NOMBRE_CATEGORIA, 'dominio': semantico.DOMINIO}, ensure_ascii=False)"
    ].join("\n"));
    return {
      nombre: "Python en el navegador (Pyodide)",
      catalogo: JSON.parse(py.globals.get("catalogo_json")()),
      compilar: async function (texto) {
        return JSON.parse(py.pyimport("compilador").compilar_json(texto));
      },
      automatas: async function () { return JSON.parse(py.pyimport("automatas").automatas_json()); }
    };
  }

  async function iniciar() {
    pintarSelectorEjemplos();
    try {
      try { motor = await motorServidor(); } catch (e) { motor = await motorNavegador(); }
      nombres = motor.catalogo.nombres;
      pintarCatalogo(motor.catalogo.catalogo);
      pintarDominio(motor.catalogo.dominio);
      pintarLeyenda();
      $("pie-motor").textContent = "Motor: " + motor.nombre;
      await cargarEjemplo(EJEMPLOS[0].archivo);
      boton.disabled = false;
      textoBoton.textContent = "Compilar reglas";
      estado.innerHTML = "<kbd>Ctrl</kbd> + <kbd>Enter</kbd> para compilar";
      motor.automatas().then(pintarAutomatas);
    } catch (e) {
      console.error(e);
      textoBoton.textContent = "No disponible";
      estado.textContent = "No se pudo cargar el compilador. Revisa tu conexión y recarga la página.";
    }
  }

  // ------------------------------------------------------------------ ejemplos y catálogos

  function pintarSelectorEjemplos() {
    var s = $("selector-ejemplo");
    s.appendChild(el("option", { value: "" }, "Cargar ejemplo…"));
    EJEMPLOS.forEach(function (e) { s.appendChild(el("option", { value: e.archivo }, e.nombre)); });
    s.addEventListener("change", function () {
      if (s.value) cargarEjemplo(s.value).then(function () { if (motor) compilarTexto(); });
      s.value = "";
    });
  }

  async function cargarEjemplo(archivoEjemplo) {
    var r = await fetch("ejemplos/" + archivoEjemplo);
    codigo.value = await r.text();
    nombre.textContent = archivoEjemplo;
  }

  function pintarCatalogo(catalogo) {
    var tb = vaciar($("tabla-catalogo"));
    catalogo.forEach(function (fila) {
      tb.appendChild(el("tr", null, [
        el("td", null, chip(fila[0], fila[1])),
        el("td", null, nombres[fila[1]]),
        el("td", { "class": "lexemas" }, fila[2]),
        el("td", { "class": "er" }, fila[3])
      ]));
    });
  }

  function pintarDominio(dominio) {
    var tb = vaciar($("tabla-dominio"));
    Object.keys(dominio.objetos).forEach(function (obj) {
      Object.keys(dominio.objetos[obj]).forEach(function (atr) {
        var info = dominio.objetos[obj][atr];
        var valores = info.tipo === "categorico" ? info.valores.join(", ")
          : (info.entero ? "entero" : "real") + (info.min != null ? " ≥ " + info.min : "") + (info.max != null ? ", ≤ " + info.max : "");
        tb.appendChild(el("tr", null, [
          el("td", { "class": "lexema" }, [el("span", { "class": "k-objeto" }, obj), "." + atr]),
          el("td", null, info.tipo === "categorico" ? "categórico" : "numérico"),
          el("td", { "class": "lexemas" }, valores)
        ]));
      });
    });
    tb.appendChild(el("tr", null, [
      el("td", { "class": "lexema" }, [el("span", { "class": "k-reservada" }, "TIEMPO"), "(…)"]),
      el("td", null, "periodo"),
      el("td", { "class": "lexemas" }, Object.keys(dominio.periodos).join(", "))
    ]));
  }

  function pintarLeyenda() {
    var ul = vaciar($("leyenda"));
    CATEGORIAS.forEach(function (c) {
      ul.appendChild(el("li", { "class": "k-" + c }, [el("i"), el("span", { style: "color: var(--tinta-suave)" }, nombres[c])]));
    });
  }

  // ------------------------------------------------------------------ compilar

  async function compilarTexto() {
    var texto = codigo.value;
    if (!texto.trim()) {
      avisar("No hay nada que compilar: escribe una regla o sube un archivo.");
      $("resultados").hidden = true;
      return;
    }
    avisar(null);
    boton.disabled = true;
    try {
      ultimo = await motor.compilar(texto);
      pintarResultado(ultimo);
    } catch (e) {
      console.error(e);
      avisar("Ocurrió un error inesperado al compilar.");
    } finally {
      boton.disabled = false;
    }
  }

  function pintarResultado(r) {
    pintarTuberia(r);
    pintarLexico(r.lexico);
    pintarSintactico(r);
    pintarSemantico(r);
    pintarJSON(r);
    var fase = r.fase_con_error;
    seleccionarPestana(fase === "léxico" || !fase ? (fase ? "panel-lexico" : "panel-json")
      : fase === "sintáctico" ? "panel-sintactico" : "panel-semantico");
    if (!fase && r.semantico && r.semantico.colisiones.length) seleccionarPestana("panel-semantico");
    var res = $("resultados");
    res.hidden = false;
    res.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function pintarTuberia(r) {
    var t = vaciar($("tuberia"));
    var sem = r.semantico;
    var fases = [
      { nombre: "Léxico", estado: r.lexico.ok ? "ok" : "error", ms: r.tiempos_ms.lexico,
        detalle: r.lexico.ok ? plural(r.lexico.tokens.length, "token", "tokens") : plural(r.lexico.errores.length, "error", "errores") },
      { nombre: "Sintáctico", estado: !r.sintactico ? "omitido" : r.sintactico.ok ? "ok" : "error", ms: r.tiempos_ms.sintactico,
        detalle: !r.sintactico ? "no se ejecutó" : r.sintactico.ok ? plural(r.sintactico.reglas.length, "regla", "reglas") : plural(r.sintactico.errores.length, "error", "errores") },
      { nombre: "Semántico", estado: !sem ? "omitido" : !sem.ok ? "error" : (sem.colisiones.length || sem.advertencias.length) ? "aviso" : "ok",
        ms: r.tiempos_ms.semantico,
        detalle: !sem ? "no se ejecutó" : !sem.ok ? plural(sem.errores.length, "error", "errores")
          : plural(sem.colisiones.length, "colisión", "colisiones") + " · " + plural(sem.advertencias.length, "advertencia", "advertencias") },
      { nombre: "JSON", estado: !sem ? "omitido" : sem.objeto_json.listo_para_activar ? "ok" : "aviso",
        detalle: !sem ? "no se generó" : sem.objeto_json.resumen.aceptadas + " de " + sem.objeto_json.resumen.reglas + " reglas aceptadas" }
    ];
    fases.forEach(function (f, i) {
      t.appendChild(el("li", { "class": "fase fase-" + f.estado }, [
        el("b", null, (i + 1) + ". " + f.nombre),
        el("span", null, f.detalle + (f.ms != null ? " · " + f.ms + " ms" : ""))
      ]));
    });

    var v = vaciar($("veredicto"));
    if (r.aceptado && sem.objeto_json.listo_para_activar) {
      v.className = "veredicto bien";
      v.textContent = "Todas las reglas son válidas y no se solapan: el objeto JSON está listo para activarse.";
    } else if (r.aceptado) {
      v.className = "veredicto aviso-texto";
      v.textContent = "Las reglas son válidas, pero hay colisiones o ramas inalcanzables que conviene revisar antes de activarlas.";
    } else {
      v.className = "veredicto mal";
      v.textContent = "La compilación se detuvo en el análisis " + r.fase_con_error + ". Corrige los errores marcados y vuelve a compilar.";
    }
  }

  // ------------------------------------------------------------------ léxico

  function pintarLexico(lx) {
    var nErr = lx.errores.length;
    var b = vaciar($("balance-lexico"));
    b.appendChild(el("b", null, lx.tokens.length));
    b.appendChild(document.createTextNode(" tokens en "));
    b.appendChild(el("b", null, lx.lineas.length));
    b.appendChild(document.createTextNode(" líneas · "));
    b.appendChild(nErr ? el("b", { "class": "mal" }, nErr + (nErr === 1 ? " error léxico" : " errores léxicos"))
      : el("b", { "class": "bien" }, "sin errores léxicos"));

    $("aviso-lexico").hidden = !nErr;
    var lista = vaciar($("lista-lexico"));
    lx.errores.forEach(function (e) { lista.appendChild(el("li", null, e)); });

    var fuente = vaciar($("fuente"));
    lx.lineas.forEach(function (linea, i) {
      var span = el("span", { "class": "linea", style: "--i: " + i });
      linea.forEach(function (frag) {
        span.appendChild(frag[1] ? el("span", { "class": "k-" + frag[1] }, frag[0]) : document.createTextNode(frag[0]));
      });
      fuente.appendChild(span);
    });

    var tt = vaciar($("tabla-tokens"));
    lx.tokens.forEach(function (t, i) {
      tt.appendChild(el("tr", null, [
        el("td", { "class": "num" }, i + 1),
        el("td", { "class": "lexema k-" + t.categoria }, t.lexema),
        el("td", null, chip(t.token, t.categoria)),
        el("td", { "class": "num" }, t.linea),
        el("td", { "class": "num" }, t.columna)
      ]));
    });

    var ts = vaciar($("tabla-resumen"));
    lx.resumen.forEach(function (fila) {
      var info = fila[1];
      var lxs = el("td", { "class": "lexemas" });
      info.lexemas.forEach(function (l) { lxs.appendChild(el("span", null, l)); });
      ts.appendChild(el("tr", null, [el("td", null, chip(fila[0], info.categoria)), lxs, el("td", { "class": "num" }, info.total)]));
    });
  }

  // ------------------------------------------------------------------ sintáctico

  function omitido(texto) { return el("p", { "class": "vacio" }, texto); }

  function listaErrores(titulo, errores) {
    var ul = el("ul");
    errores.forEach(function (e) { ul.appendChild(el("li", null, e.mensaje)); });
    return el("div", { "class": "aviso", role: "alert" }, [el("strong", null, titulo), ul]);
  }

  function pintarSintactico(r) {
    var c = vaciar($("sintactico-contenido"));
    var s = r.sintactico;
    if (!s) { c.appendChild(omitido("No se ejecutó: primero corrige los errores léxicos.")); return; }
    if (!s.ok) {
      c.appendChild(listaErrores("Las reglas no cumplen la gramática.", s.errores));
      c.appendChild(el("p", { "class": "nota" }, "Los errores los detecta el analizador sintáctico generado por ANTLR a partir de gramatica/ReglasDescuento.g4."));
      return;
    }
    c.appendChild(el("p", { "class": "balance" }, [
      el("b", { "class": "bien" }, s.reglas.length + (s.reglas.length === 1 ? " regla" : " reglas")),
      " aceptadas por la gramática · árbol del programa con " + s.nodos_programa + " nodos"
    ]));

    var selector = el("div", { "class": "selector-tokens", role: "tablist", "aria-label": "Reglas" });
    var detalle = el("div");
    s.reglas.forEach(function (regla, i) {
      var b = el("button", { type: "button", "class": "chip-boton", "aria-selected": i === 0 ? "true" : "false" }, regla.id + " · línea " + regla.linea);
      b.addEventListener("click", function () {
        selector.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-selected", "false"); });
        b.setAttribute("aria-selected", "true");
        pintarRegla(detalle, regla);
      });
      selector.appendChild(b);
    });
    c.appendChild(selector);
    c.appendChild(detalle);
    pintarRegla(detalle, s.reglas[0]);

    // Para imprimir: todas las reglas.
    var imprimir = el("div", { "class": "solo-imprimir" });
    s.reglas.slice(1).forEach(function (regla) { var d = el("div"); pintarRegla(d, regla); imprimir.appendChild(d); });
    c.appendChild(imprimir);
  }

  function pintarRegla(destino, regla) {
    vaciar(destino);
    destino.appendChild(el("h3", null, "Regla " + regla.id + " (línea " + regla.linea + ")"));
    destino.appendChild(el("pre", { "class": "muestra compacta" }, regla.texto));
    destino.appendChild(el("h3", null, "Árbol de derivación"));
    destino.appendChild(grafo(regla.arbol_dot, "Árbol de derivación de " + regla.id));
    var cols = el("div", { "class": "tablas" });
    [["Derivación por la izquierda", regla.derivacion_izquierda], ["Derivación por la derecha", regla.derivacion_derecha]].forEach(function (par) {
      var ol = el("ol", { "class": "derivacion" });
      par[1].forEach(function (p, i) {
        ol.appendChild(el("li", null, [
          p.produccion ? el("span", { "class": "produccion" }, p.produccion) : el("span", { "class": "produccion" }, "inicio"),
          el("code", null, (i ? "⇒ " : "") + p.forma)
        ]));
      });
      cols.appendChild(el("div", null, [el("h3", null, par[0] + " (" + (par[1].length - 1) + " pasos)"), el("div", { "class": "marco-tabla alto" }, ol)]));
    });
    destino.appendChild(cols);
  }

  // ------------------------------------------------------------------ semántico

  var ESTADOS = { aceptada: ["Aceptada", "bien"], en_colision: ["En colisión", "aviso-texto"], rechazada: ["Rechazada", "mal"] };

  function pintarSemantico(r) {
    var c = vaciar($("semantico-contenido"));
    var s = r.semantico;
    if (!s) { c.appendChild(omitido("No se ejecutó: primero corrige los errores " + r.fase_con_error + "s.")); return; }

    if (s.errores.length) c.appendChild(listaErrores("Errores semánticos", s.errores));

    if (s.advertencias.length) {
      var ul = el("ul");
      s.advertencias.forEach(function (a) { ul.appendChild(el("li", null, a.mensaje)); });
      c.appendChild(el("div", { "class": "aviso aviso-suave" }, [el("strong", null, "Ambigüedades (advertencias)"), ul]));
    }

    c.appendChild(el("h3", null, "Colisiones entre reglas"));
    if (!s.colisiones.length) {
      c.appendChild(el("p", { "class": "nota" }, s.ok ? "Ninguna: no hay dos reglas que puedan aplicar descuento a la misma transacción."
        : "Solo se buscan colisiones entre reglas sin errores."));
    } else {
      c.appendChild(el("p", { "class": "nota" }, "Pares de reglas que pueden aplicarse a la misma compra y acumular descuentos. El ejemplo es una transacción concreta que activa ambas."));
      c.appendChild(tabla(["Reglas", "Ramas", "Descuentos", "Acumulado", "Ejemplo de transacción"], s.colisiones.map(function (col) {
        return el("tr", null, [
          el("td", { "class": "lexema" }, col.reglas.join(" y ") + (col.duplicada ? " (duplicadas)" : "")),
          el("td", null, col.ramas.join(" / ")),
          el("td", { "class": "lexema" }, col.descuentos.map(function (d) { return d + "%"; }).join(" + ")),
          el("td", { "class": "lexema mal" }, col.acumulado + "%"),
          el("td", { "class": "lexemas" }, col.ejemplo)
        ]);
      })));
    }

    c.appendChild(el("h3", null, "Estado de cada regla"));
    c.appendChild(tabla(["Regla", "Línea", "Estado", "Texto"], s.objeto_json.reglas.map(function (rg) {
      var e = ESTADOS[rg.estado];
      return el("tr", null, [
        el("td", { "class": "lexema" }, rg.id),
        el("td", { "class": "num" }, rg.linea),
        el("td", null, el("b", { "class": e[1] }, e[0])),
        el("td", { "class": "lexemas" }, rg.texto)
      ]);
    })));
  }

  // ------------------------------------------------------------------ JSON

  function pintarJSON(r) {
    var c = vaciar($("json-contenido"));
    var s = r.semantico;
    if (!s) { c.appendChild(omitido("No se generó: la compilación se detuvo en el análisis " + r.fase_con_error + ".")); return; }
    var texto = JSON.stringify(s.objeto_json, null, 2);
    var barra = el("div", { "class": "barra-json no-imprimir" });
    var descargar = el("button", { type: "button", "class": "boton" }, "Descargar reglas.json");
    descargar.addEventListener("click", function () {
      var url = URL.createObjectURL(new Blob([texto], { type: "application/json" }));
      var a = el("a", { href: url, download: "reglas.json" });
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    });
    var copiar = el("button", { type: "button", "class": "boton" }, "Copiar");
    copiar.addEventListener("click", function () {
      navigator.clipboard.writeText(texto).then(function () { copiar.textContent = "Copiado"; setTimeout(function () { copiar.textContent = "Copiar"; }, 1500); });
    });
    barra.appendChild(descargar);
    barra.appendChild(copiar);
    barra.appendChild(el("span", { "class": "ayuda" }, s.objeto_json.listo_para_activar
      ? "Listo para activar en el motor de reglas." : "Incluye el estado de cada regla; solo las aceptadas deberían activarse."));
    c.appendChild(barra);
    c.appendChild(el("pre", { "class": "json" }, texto));
  }

  // ------------------------------------------------------------------ pestañas

  function seleccionarPestana(id) {
    document.querySelectorAll(".pestana").forEach(function (p) { p.setAttribute("aria-selected", p.dataset.panel === id ? "true" : "false"); });
    document.querySelectorAll("#resultados .panel").forEach(function (p) { p.classList.toggle("activo", p.id === id); });
  }
  document.querySelectorAll(".pestana").forEach(function (p) {
    p.addEventListener("click", function () { seleccionarPestana(p.dataset.panel); });
  });

  // ------------------------------------------------------------------ autómatas

  var VISTAS = [["afnd", "AFND (Thompson)"], ["afd", "AFD (subconjuntos)"], ["minimo", "AFD mínimo"]];

  function pintarAutomatas(datos) {
    var sel = vaciar($("selector-tokens"));
    datos.tokens.forEach(function (t, i) {
      var b = el("button", { type: "button", "class": "chip-boton k-" + t.categoria, "aria-selected": i === 0 ? "true" : "false" }, t.token);
      b.addEventListener("click", function () {
        sel.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-selected", "false"); });
        b.setAttribute("aria-selected", "true");
        pintarAutomata(t);
      });
      sel.appendChild(b);
    });
    pintarAutomata(datos.tokens[0]);
  }

  function pintarAutomata(t, vista) {
    vista = vista || "afnd";
    var c = vaciar($("automata-detalle"));
    c.appendChild(el("div", { "class": "ficha-er" }, [
      el("div", null, [el("span", { "class": "ayuda" }, "Token"), el("b", null, chip(t.token, t.categoria))]),
      el("div", null, [el("span", { "class": "ayuda" }, "Expresión regular"), el("code", { "class": "er-grande" }, t.er)]),
      el("div", null, [el("span", { "class": "ayuda" }, "Estados"), el("span", null, "AFND " + t.afnd.estados + " · AFD " + t.afd.estados + " · mínimo " + t.minimo.estados)])
    ]));

    var pest = el("div", { "class": "pestanas", role: "tablist" });
    VISTAS.forEach(function (v) {
      var b = el("button", { role: "tab", "class": "pestana", "aria-selected": v[0] === vista ? "true" : "false" }, v[1]);
      b.addEventListener("click", function () { pintarAutomata(t, v[0]); });
      pest.appendChild(b);
    });
    c.appendChild(pest);

    var a = t[vista];
    c.appendChild(grafo(a.dot, VISTAS.filter(function (v) { return v[0] === vista; })[0][1] + " de " + t.token));

    var cols = el("div", { "class": "tablas" });
    var izq = el("div", null, el("h3", null, "Tabla de transiciones"));
    izq.appendChild(tabla(["Estado"].concat(a.tabla.columnas), a.tabla.filas.map(function (f) {
      return el("tr", null, [el("td", { "class": "lexema" }, f.marca + f.estado)].concat(f.celdas.map(function (x) {
        return el("td", { "class": "lexema" + (x === "-" ? " tenue" : "") }, x);
      })));
    })));
    izq.appendChild(el("p", { "class": "nota" }, "→ estado inicial · * estado de aceptación · - sin transición"));
    if (a.subconjuntos) {
      izq.appendChild(el("h3", null, vista === "afd" ? "Estados del AFD (subconjuntos del AFND)" : "Estados del mínimo (bloques del AFD)"));
      var ul = el("ul", { "class": "subconjuntos" });
      Object.keys(a.subconjuntos).forEach(function (k) { ul.appendChild(el("li", null, [el("b", null, k), " = {" + a.subconjuntos[k].join(", ") + "}"])); });
      izq.appendChild(ul);
    }
    cols.appendChild(izq);

    var q = a.quintupla;
    var der = el("div", null, el("h3", null, "Quíntupla M = (Q, Σ, δ, q0, F)"));
    var dl = el("dl", { "class": "quintupla" });
    [["Q", q.Q], ["Σ", q["Σ"]], ["q0", q.q0], ["F", q.F]].forEach(function (p) { dl.appendChild(el("dt", null, p[0])); dl.appendChild(el("dd", null, p[1])); });
    dl.appendChild(el("dt", null, "δ"));
    var dd = el("dd");
    q["δ"].forEach(function (d) { dd.appendChild(el("div", null, d)); });
    dl.appendChild(dd);
    der.appendChild(dl);
    if (vista !== "afnd") der.appendChild(probador(t, a));
    cols.appendChild(der);
    c.appendChild(cols);
  }

  // Simula el AFD con su propia tabla de transiciones.
  function probador(t, a) {
    var caja = el("div", { "class": "probador" });
    caja.appendChild(el("h3", null, "Probar una cadena"));
    var entrada = el("input", { type: "text", "class": "entrada", value: (t.ejemplos.split(",")[0] || "").trim(), "aria-label": "Cadena a probar", spellcheck: "false" });
    var salida = el("p", { "class": "nota" });
    function simbolo(ch) {
      if (t.clases && /[A-Za-z]/.test(ch)) return "L";
      if (t.clases && /[0-9]/.test(ch)) return "D";
      return ch;
    }
    function probar() {
      var col = {}, fila = {};
      a.tabla.columnas.forEach(function (s, i) { col[s] = i; });
      a.tabla.filas.forEach(function (f) { fila[f.estado] = f; });
      var actual = a.quintupla.q0, camino = [actual];
      for (var i = 0; i < entrada.value.length; i++) {
        var s = simbolo(entrada.value[i]);
        var sig = col[s] == null ? "-" : fila[actual].celdas[col[s]];
        camino.push(sig);
        if (sig === "-") break;
        actual = sig;
      }
      var acepta = camino[camino.length - 1] !== "-" && fila[actual].marca.indexOf("*") !== -1 && entrada.value.length > 0;
      vaciar(salida).appendChild(el("b", { "class": acepta ? "bien" : "mal" }, acepta ? "Aceptada" : "Rechazada"));
      salida.appendChild(document.createTextNode(" · recorrido: " + camino.join(" → ")));
    }
    entrada.addEventListener("input", probar);
    caja.appendChild(entrada);
    caja.appendChild(salida);
    probar();
    return caja;
  }

  // ------------------------------------------------------------------ eventos

  archivo.addEventListener("change", function () {
    var f = archivo.files[0];
    if (!f) return;
    var ext = f.name.slice(f.name.lastIndexOf(".")).toLowerCase();
    if (EXTENSIONES.indexOf(ext) === -1) { avisar("El archivo «" + f.name + "» no es válido. Sube un archivo .dsl, .txt o .reglas."); archivo.value = ""; return; }
    if (f.size > 256 * 1024) { avisar("El archivo supera el límite de 256 KB."); archivo.value = ""; return; }
    var lector = new FileReader();
    lector.onload = function () {
      codigo.value = lector.result;
      nombre.textContent = f.name;
      avisar(null);
      if (motor) compilarTexto();
    };
    lector.readAsText(f, "utf-8");
    archivo.value = "";
  });

  $("limpiar").addEventListener("click", function () {
    codigo.value = "";
    nombre.textContent = "reglas.dsl";
    $("resultados").hidden = true;
    codigo.focus();
  });

  $("imprimir").addEventListener("click", function () { window.print(); });

  codigo.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); if (motor) compilarTexto(); }
  });

  form.addEventListener("submit", function (e) { e.preventDefault(); if (motor) compilarTexto(); });

  iniciar();
})();
