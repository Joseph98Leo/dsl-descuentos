// Archivo de prueba con errores léxicos (caracteres fuera del alfabeto)
SI CLIENTE.nivel = VIP & COMPRA.total > $500 ENTONCES APLICAR DESCUENTO(15%)
SI COMPRA.total >= 200 ENTONCES APLICAR DESCUENTO(8.5%) ;
