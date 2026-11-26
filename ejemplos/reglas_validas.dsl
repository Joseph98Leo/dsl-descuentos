// Campaña Navidad 2026 - reglas sin solapamientos
// Los clientes VIP tienen su propia escala; el resto recibe descuento por categoría.
SI CLIENTE.nivel = VIP Y COMPRA.total > 500 ENTONCES APLICAR DESCUENTO(15%)
SINO SI CLIENTE.nivel = VIP ENTONCES APLICAR DESCUENTO(10%)
SINO APLICAR DESCUENTO(0%)

SI CLIENTE.nivel != VIP Y COMPRA.categoria = electronica Y TIEMPO(navidad) ENTONCES APLICAR DESCUENTO(8%)

SI CLIENTE.nivel != VIP Y NO (COMPRA.categoria == electronica) Y COMPRA.cantidad >= 3 ENTONCES APLICAR DESCUENTO(5%)
