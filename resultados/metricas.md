# Resultados de la evaluación

Generado el 2026-11-26T00:28:00 con `python evaluar.py`.

| Objetivo | Indicador | Meta | Resultado |
|---|---|---|---|
| OE1 | Tokens modelados (ER, AFND, AFD, quíntupla) | ≥ 15 | 17 |
| OE2 | Cadenas de prueba clasificadas correctamente | ≥ 5 cadenas | 34 de 34 (100.0 %) |
| OE3 | Solapamientos configurados detectados | ≥ 90 % | 13 de 13 (100.0 %), 0 falsos positivos |
| OE4 | Objetos JSON generados | uno por regla | 13 |
| OE5 | Pruebas automatizadas exitosas | > 95 % | 80 de 80 (100.0 %) |
| RNF | Tiempo de análisis por regla | < 200 ms | promedio 0.28 ms, máximo 0.98 ms |

## OE1 · Autómatas por token

| Token | Expresión regular | Estados AFND | Estados AFD | Estados AFD mínimo |
|---|---|---|---|---|
| T_SI | `SI` | 3 | 3 | 3 |
| T_SINO | `SINO` | 5 | 5 | 5 |
| T_ENTONCES | `ENTONCES` | 9 | 9 | 9 |
| T_APLICAR | `APLICAR` | 8 | 8 | 8 |
| T_DESCUENTO | `DESCUENTO` | 10 | 10 | 10 |
| T_AND | `Y` | 2 | 2 | 2 |
| T_OR | `O` | 2 | 2 | 2 |
| T_NOT | `NO` | 3 | 3 | 3 |
| T_OBJETO | `(CLIENTE\|COMPRA)` | 17 | 13 | 12 |
| T_TIEMPO | `TIEMPO` | 7 | 7 | 7 |
| T_ID | `(L\|_)(L\|D\|_)*` | 15 | 6 | 2 |
| T_NUM | `D+` | 4 | 2 | 2 |
| T_PORCENTAJE | `D+%` | 5 | 3 | 3 |
| T_RELOP | `= \| == \| != \| >(=)? \| <(=)?` | 20 | 9 | 4 |
| T_PUNTO | `\.` | 2 | 2 | 2 |
| T_PARI | `\(` | 2 | 2 | 2 |
| T_PARD | `\)` | 2 | 2 | 2 |

## OE2 · Cadenas de prueba

| Cadena | Esperado | Obtenido | Correcto |
|---|---|---|---|
| `SI CLIENTE.nivel = VIP ENTONCES APLICAR DESCUENTO(15%)` | aceptada | aceptada | Sí |
| `SI CLIENTE.nivel = VIP Y COMPRA.total > 500 Y TIEMPO(enrango) ENTONCES APLICAR DESCUENTO(15%)` | aceptada | aceptada | Sí |
| `SI CLIENTE.nivel = VIP ENTONCES APLICAR DESCUENTO(15%) SINO SI COMPRA.total > 500 ENTONCES APLICAR DESCUENTO(10%) SINO APLICAR DESCUENTO(0%)` | aceptada | aceptada | Sí |
| `SI COMPRA.total >= 300 ENTONCES APLICAR DESCUENTO(10%) SINO APLICAR DESCUENTO(0%)` | aceptada | aceptada | Sí |
| `SI NO (CLIENTE.tipo == nuevo) O COMPRA.cantidad != 1 ENTONCES APLICAR DESCUENTO(5%)` | aceptada | aceptada | Sí |
| `SI (CLIENTE.nivel = ORO O CLIENTE.nivel = PLATA) Y COMPRA.total > 200 ENTONCES APLICAR DESCUENTO(7%)` | aceptada | aceptada | Sí |
| `SI NO NO TIEMPO(navidad) ENTONCES APLICAR DESCUENTO(3%)` | aceptada | aceptada | Sí |
| `SI CLIENTE.edad >= 60 ENTONCES APLICAR DESCUENTO(12%)` | aceptada | aceptada | Sí |
| `SI COMPRA.canal = app Y COMPRA.cantidad <= 2 ENTONCES APLICAR DESCUENTO(4%)` | aceptada | aceptada | Sí |
| `// comentario ⏎ SI COMPRA.total < 50 ENTONCES APLICAR DESCUENTO(1%) ⏎ SI COMPRA.total > 1000 ENTONCES APLICAR DESCUENTO(20%)` | aceptada | aceptada | Sí |
| `SI CLIENTE.compras > 10 ENTONCES APLICAR DESCUENTO(6%) SINO SI CLIENTE.compras > 5 ENTONCES APLICAR DESCUENTO(3%)` | aceptada | aceptada | Sí |
| `SI ((COMPRA.total > 100)) ENTONCES APLICAR DESCUENTO(2%)` | aceptada | aceptada | Sí |
| `SI CLIENTE.nivel = VIP & COMPRA.total > 500 ENTONCES APLICAR DESCUENTO(15%)` | rechazada (léxico) | rechazada (léxico) | Sí |
| `SI COMPRA.total > $500 ENTONCES APLICAR DESCUENTO(15%)` | rechazada (léxico) | rechazada (léxico) | Sí |
| `SI COMPRA.total >= 200 ENTONCES APLICAR DESCUENTO(8.5%) ;` | rechazada (léxico) | rechazada (léxico) | Sí |
| `SI CLIENTE.nivel = VIP COMPRA.total > 500 ENTONCES APLICAR DESCUENTO(15%)` | rechazada (sintáctico) | rechazada (sintáctico) | Sí |
| `SI COMPRA.total >= 300 ENTONCES DESCUENTO(10%)` | rechazada (sintáctico) | rechazada (sintáctico) | Sí |
| `SI COMPRA.total > 500 APLICAR DESCUENTO(10%)` | rechazada (sintáctico) | rechazada (sintáctico) | Sí |
| `SI COMPRA.total > 500 ENTONCES APLICAR DESCUENTO(10)` | rechazada (sintáctico) | rechazada (sintáctico) | Sí |
| `SI total > 500 ENTONCES APLICAR DESCUENTO(10%)` | rechazada (sintáctico) | rechazada (sintáctico) | Sí |
| `SI COMPRA.total > ENTONCES APLICAR DESCUENTO(10%)` | rechazada (sintáctico) | rechazada (sintáctico) | Sí |
| `SI (COMPRA.total > 500 ENTONCES APLICAR DESCUENTO(10%)` | rechazada (sintáctico) | rechazada (sintáctico) | Sí |
| `SINO APLICAR DESCUENTO(10%)` | rechazada (sintáctico) | rechazada (sintáctico) | Sí |
| `SI COMPRA.total > 500 ENTONCES APLICAR DESCUENTO(10%) SINO` | rechazada (sintáctico) | rechazada (sintáctico) | Sí |
| `si COMPRA.total > 500 ENTONCES APLICAR DESCUENTO(10%)` | rechazada (sintáctico) | rechazada (sintáctico) | Sí |
| `SI COMPRA.total > 500 Y ENTONCES APLICAR DESCUENTO(10%)` | rechazada (sintáctico) | rechazada (sintáctico) | Sí |
| `SI CLIENTE.saldo > 100 ENTONCES APLICAR DESCUENTO(5%)` | rechazada (semántico) | rechazada (semántico) | Sí |
| `SI COMPRA.total > 500 Y COMPRA.total < 100 ENTONCES APLICAR DESCUENTO(10%)` | rechazada (semántico) | rechazada (semántico) | Sí |
| `SI CLIENTE.nivel = DIAMANTE ENTONCES APLICAR DESCUENTO(10%)` | rechazada (semántico) | rechazada (semántico) | Sí |
| `SI CLIENTE.nivel = VIP ENTONCES APLICAR DESCUENTO(120%)` | rechazada (semántico) | rechazada (semántico) | Sí |
| `SI TIEMPO(verano) ENTONCES APLICAR DESCUENTO(5%)` | rechazada (semántico) | rechazada (semántico) | Sí |
| `SI COMPRA.total = VIP ENTONCES APLICAR DESCUENTO(5%)` | rechazada (semántico) | rechazada (semántico) | Sí |
| `SI CLIENTE.nivel > 5 ENTONCES APLICAR DESCUENTO(5%)` | rechazada (semántico) | rechazada (semántico) | Sí |
| `SI COMPRA.cantidad < 1 ENTONCES APLICAR DESCUENTO(5%)` | rechazada (semántico) | rechazada (semántico) | Sí |

## OE3 · Detección de colisiones

| Caso | Esperadas | Detectadas | Falsos positivos |
|---|---|---|---|
| Mismo segmento con dos descuentos | 1 | 1 | 0 |
| Reglas duplicadas | 1 | 1 | 0 |
| Intervalos que se cruzan | 1 | 1 | 0 |
| Intervalos que se tocan en un punto | 1 | 1 | 0 |
| Intervalos contiguos sin cruce | 0 | 0 | 0 |
| Campaña por tiempo y por categoría | 1 | 1 | 0 |
| Segmentos excluyentes por nivel | 0 | 0 | 0 |
| Negación que deja hueco | 1 | 1 | 0 |
| Rama SINO SI que choca con otra regla | 1 | 1 | 0 |
| Rama SINO SI excluida por la rama anterior | 1 | 1 | 0 |
| Descuento 0% no cuenta como colisión | 0 | 0 | 0 |
| Atributo entero sin valores en común | 0 | 0 | 0 |
| Tres reglas, dos colisiones | 4 | 4 | 0 |
| Disyunción con una rama en común | 1 | 1 | 0 |
| Edad en rangos excluyentes | 0 | 0 | 0 |
