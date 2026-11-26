/*
 * Gramática del DSL de reglas de descuento (Etapa 3).
 * Especificación para el metacompilador ANTLR 4.13.2.
 *
 * Las reglas sintácticas son la GLC del informe (sección 8.2.3), escritas en
 * notación ANTLR. Los nombres de los tokens son los mismos del informe (8.2.1).
 * ANTLR admite la recursión por la izquierda directa de CONDICION y TERMINO,
 * así que la gramática se mantiene igual que en el informe.
 *
 * Regenerar el analizador:  bash herramientas/generar_parser.sh
 */
grammar ReglasDescuento;

// ---------------------------------------------------------------- Sintaxis

// Símbolo inicial auxiliar: obliga a consumir toda la entrada.
inicio          : programa EOF ;

// PROGRAMA → REGLA PROGRAMA | REGLA
// Escrita con el prefijo común factorizado (REGLA PROGRAMA?): genera el mismo
// lenguaje y el mismo árbol, pero ANTLR decide con un solo token de anticipación
// (SI o fin de archivo) y así reporta cada error en la regla donde ocurre.
programa        : regla programa? ;

// REGLA → T_SI CONDICION T_ENTONCES ACCION RESTO
regla           : T_SI condicion T_ENTONCES accion resto ;

// RESTO → T_SINO T_SI CONDICION T_ENTONCES ACCION RESTO | T_SINO ACCION | ε
resto           : T_SINO T_SI condicion T_ENTONCES accion resto
                | T_SINO accion
                | /* ε */
                ;

// CONDICION → CONDICION T_OR TERMINO | TERMINO
condicion       : condicion T_OR termino
                | termino
                ;

// TERMINO → TERMINO T_AND FACTOR | FACTOR
termino         : termino T_AND factor
                | factor
                ;

// FACTOR → T_NOT FACTOR | T_PARI CONDICION T_PARD | COMPARACION | FUNCION_TIEMPO
factor          : T_NOT factor
                | T_PARI condicion T_PARD
                | comparacion
                | funcion_tiempo
                ;

// COMPARACION → ATRIBUTO T_RELOP OPERANDO
comparacion     : atributo T_RELOP operando ;

// ATRIBUTO → T_OBJETO T_PUNTO T_ID
atributo        : T_OBJETO T_PUNTO T_ID ;

// FUNCION_TIEMPO → T_TIEMPO T_PARI T_ID T_PARD
funcion_tiempo  : T_TIEMPO T_PARI T_ID T_PARD ;

// OPERANDO → T_ID | T_NUM | T_PORCENTAJE
operando        : T_ID
                | T_NUM
                | T_PORCENTAJE
                ;

// ACCION → T_APLICAR T_DESCUENTO T_PARI T_PORCENTAJE T_PARD
accion          : T_APLICAR T_DESCUENTO T_PARI T_PORCENTAJE T_PARD ;

// ---------------------------------------------------------------- Léxico
// ANTLR aplica la coincidencia más larga y, a igual longitud, la regla que
// aparece primero: por eso las palabras reservadas van antes que T_ID.

T_SINO          : 'SINO' ;
T_SI            : 'SI' ;
T_ENTONCES      : 'ENTONCES' ;
T_APLICAR       : 'APLICAR' ;
T_DESCUENTO     : 'DESCUENTO' ;
T_AND           : 'Y' ;
T_OR            : 'O' ;
T_NOT           : 'NO' ;
T_OBJETO        : 'CLIENTE' | 'COMPRA' ;
T_TIEMPO        : 'TIEMPO' ;
T_ID            : [a-zA-Z_] [a-zA-Z0-9_]* ;          // (L|_)(L|D|_)*
T_PORCENTAJE    : [0-9]+ '%' ;                        // D+%
T_NUM           : [0-9]+ ;                            // D+
T_RELOP         : '>=' | '<=' | '==' | '!=' | '=' | '>' | '<' ;
T_PUNTO         : '.' ;
T_PARI          : '(' ;
T_PARD          : ')' ;

COMENTARIO      : '//' ~[\r\n]* -> skip ;
ESPACIO         : [ \t\r\n]+ -> skip ;
