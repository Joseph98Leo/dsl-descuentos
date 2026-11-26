# Generated from ReglasDescuento.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .ReglasDescuentoParser import ReglasDescuentoParser
else:
    from ReglasDescuentoParser import ReglasDescuentoParser

# This class defines a complete generic visitor for a parse tree produced by ReglasDescuentoParser.

class ReglasDescuentoVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ReglasDescuentoParser#inicio.
    def visitInicio(self, ctx:ReglasDescuentoParser.InicioContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ReglasDescuentoParser#programa.
    def visitPrograma(self, ctx:ReglasDescuentoParser.ProgramaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ReglasDescuentoParser#regla.
    def visitRegla(self, ctx:ReglasDescuentoParser.ReglaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ReglasDescuentoParser#resto.
    def visitResto(self, ctx:ReglasDescuentoParser.RestoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ReglasDescuentoParser#condicion.
    def visitCondicion(self, ctx:ReglasDescuentoParser.CondicionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ReglasDescuentoParser#termino.
    def visitTermino(self, ctx:ReglasDescuentoParser.TerminoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ReglasDescuentoParser#factor.
    def visitFactor(self, ctx:ReglasDescuentoParser.FactorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ReglasDescuentoParser#comparacion.
    def visitComparacion(self, ctx:ReglasDescuentoParser.ComparacionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ReglasDescuentoParser#atributo.
    def visitAtributo(self, ctx:ReglasDescuentoParser.AtributoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ReglasDescuentoParser#funcion_tiempo.
    def visitFuncion_tiempo(self, ctx:ReglasDescuentoParser.Funcion_tiempoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ReglasDescuentoParser#operando.
    def visitOperando(self, ctx:ReglasDescuentoParser.OperandoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ReglasDescuentoParser#accion.
    def visitAccion(self, ctx:ReglasDescuentoParser.AccionContext):
        return self.visitChildren(ctx)



del ReglasDescuentoParser