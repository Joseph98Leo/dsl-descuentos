# Generated from ReglasDescuento.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,19,103,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,1,0,1,0,1,0,1,1,1,
        1,3,1,30,8,1,1,2,1,2,1,2,1,2,1,2,1,2,1,3,1,3,1,3,1,3,1,3,1,3,1,3,
        1,3,1,3,1,3,3,3,48,8,3,1,4,1,4,1,4,1,4,1,4,1,4,5,4,56,8,4,10,4,12,
        4,59,9,4,1,5,1,5,1,5,1,5,1,5,1,5,5,5,67,8,5,10,5,12,5,70,9,5,1,6,
        1,6,1,6,1,6,1,6,1,6,1,6,1,6,3,6,80,8,6,1,7,1,7,1,7,1,7,1,8,1,8,1,
        8,1,8,1,9,1,9,1,9,1,9,1,9,1,10,1,10,1,11,1,11,1,11,1,11,1,11,1,11,
        1,11,0,2,8,10,12,0,2,4,6,8,10,12,14,16,18,20,22,0,1,1,0,11,13,98,
        0,24,1,0,0,0,2,27,1,0,0,0,4,31,1,0,0,0,6,47,1,0,0,0,8,49,1,0,0,0,
        10,60,1,0,0,0,12,79,1,0,0,0,14,81,1,0,0,0,16,85,1,0,0,0,18,89,1,
        0,0,0,20,94,1,0,0,0,22,96,1,0,0,0,24,25,3,2,1,0,25,26,5,0,0,1,26,
        1,1,0,0,0,27,29,3,4,2,0,28,30,3,2,1,0,29,28,1,0,0,0,29,30,1,0,0,
        0,30,3,1,0,0,0,31,32,5,2,0,0,32,33,3,8,4,0,33,34,5,3,0,0,34,35,3,
        22,11,0,35,36,3,6,3,0,36,5,1,0,0,0,37,38,5,1,0,0,38,39,5,2,0,0,39,
        40,3,8,4,0,40,41,5,3,0,0,41,42,3,22,11,0,42,43,3,6,3,0,43,48,1,0,
        0,0,44,45,5,1,0,0,45,48,3,22,11,0,46,48,1,0,0,0,47,37,1,0,0,0,47,
        44,1,0,0,0,47,46,1,0,0,0,48,7,1,0,0,0,49,50,6,4,-1,0,50,51,3,10,
        5,0,51,57,1,0,0,0,52,53,10,2,0,0,53,54,5,7,0,0,54,56,3,10,5,0,55,
        52,1,0,0,0,56,59,1,0,0,0,57,55,1,0,0,0,57,58,1,0,0,0,58,9,1,0,0,
        0,59,57,1,0,0,0,60,61,6,5,-1,0,61,62,3,12,6,0,62,68,1,0,0,0,63,64,
        10,2,0,0,64,65,5,6,0,0,65,67,3,12,6,0,66,63,1,0,0,0,67,70,1,0,0,
        0,68,66,1,0,0,0,68,69,1,0,0,0,69,11,1,0,0,0,70,68,1,0,0,0,71,72,
        5,8,0,0,72,80,3,12,6,0,73,74,5,16,0,0,74,75,3,8,4,0,75,76,5,17,0,
        0,76,80,1,0,0,0,77,80,3,14,7,0,78,80,3,18,9,0,79,71,1,0,0,0,79,73,
        1,0,0,0,79,77,1,0,0,0,79,78,1,0,0,0,80,13,1,0,0,0,81,82,3,16,8,0,
        82,83,5,14,0,0,83,84,3,20,10,0,84,15,1,0,0,0,85,86,5,9,0,0,86,87,
        5,15,0,0,87,88,5,11,0,0,88,17,1,0,0,0,89,90,5,10,0,0,90,91,5,16,
        0,0,91,92,5,11,0,0,92,93,5,17,0,0,93,19,1,0,0,0,94,95,7,0,0,0,95,
        21,1,0,0,0,96,97,5,4,0,0,97,98,5,5,0,0,98,99,5,16,0,0,99,100,5,12,
        0,0,100,101,5,17,0,0,101,23,1,0,0,0,5,29,47,57,68,79
    ]

class ReglasDescuentoParser ( Parser ):

    grammarFileName = "ReglasDescuento.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'SINO'", "'SI'", "'ENTONCES'", "'APLICAR'", 
                     "'DESCUENTO'", "'Y'", "'O'", "'NO'", "<INVALID>", "'TIEMPO'", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'.'", "'('", "')'" ]

    symbolicNames = [ "<INVALID>", "T_SINO", "T_SI", "T_ENTONCES", "T_APLICAR", 
                      "T_DESCUENTO", "T_AND", "T_OR", "T_NOT", "T_OBJETO", 
                      "T_TIEMPO", "T_ID", "T_PORCENTAJE", "T_NUM", "T_RELOP", 
                      "T_PUNTO", "T_PARI", "T_PARD", "COMENTARIO", "ESPACIO" ]

    RULE_inicio = 0
    RULE_programa = 1
    RULE_regla = 2
    RULE_resto = 3
    RULE_condicion = 4
    RULE_termino = 5
    RULE_factor = 6
    RULE_comparacion = 7
    RULE_atributo = 8
    RULE_funcion_tiempo = 9
    RULE_operando = 10
    RULE_accion = 11

    ruleNames =  [ "inicio", "programa", "regla", "resto", "condicion", 
                   "termino", "factor", "comparacion", "atributo", "funcion_tiempo", 
                   "operando", "accion" ]

    EOF = Token.EOF
    T_SINO=1
    T_SI=2
    T_ENTONCES=3
    T_APLICAR=4
    T_DESCUENTO=5
    T_AND=6
    T_OR=7
    T_NOT=8
    T_OBJETO=9
    T_TIEMPO=10
    T_ID=11
    T_PORCENTAJE=12
    T_NUM=13
    T_RELOP=14
    T_PUNTO=15
    T_PARI=16
    T_PARD=17
    COMENTARIO=18
    ESPACIO=19

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class InicioContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def programa(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.ProgramaContext,0)


        def EOF(self):
            return self.getToken(ReglasDescuentoParser.EOF, 0)

        def getRuleIndex(self):
            return ReglasDescuentoParser.RULE_inicio

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInicio" ):
                return visitor.visitInicio(self)
            else:
                return visitor.visitChildren(self)




    def inicio(self):

        localctx = ReglasDescuentoParser.InicioContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_inicio)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 24
            self.programa()
            self.state = 25
            self.match(ReglasDescuentoParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ProgramaContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def regla(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.ReglaContext,0)


        def programa(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.ProgramaContext,0)


        def getRuleIndex(self):
            return ReglasDescuentoParser.RULE_programa

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPrograma" ):
                return visitor.visitPrograma(self)
            else:
                return visitor.visitChildren(self)




    def programa(self):

        localctx = ReglasDescuentoParser.ProgramaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_programa)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 27
            self.regla()
            self.state = 29
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2:
                self.state = 28
                self.programa()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ReglaContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def T_SI(self):
            return self.getToken(ReglasDescuentoParser.T_SI, 0)

        def condicion(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.CondicionContext,0)


        def T_ENTONCES(self):
            return self.getToken(ReglasDescuentoParser.T_ENTONCES, 0)

        def accion(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.AccionContext,0)


        def resto(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.RestoContext,0)


        def getRuleIndex(self):
            return ReglasDescuentoParser.RULE_regla

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRegla" ):
                return visitor.visitRegla(self)
            else:
                return visitor.visitChildren(self)




    def regla(self):

        localctx = ReglasDescuentoParser.ReglaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_regla)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 31
            self.match(ReglasDescuentoParser.T_SI)
            self.state = 32
            self.condicion(0)
            self.state = 33
            self.match(ReglasDescuentoParser.T_ENTONCES)
            self.state = 34
            self.accion()
            self.state = 35
            self.resto()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RestoContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def T_SINO(self):
            return self.getToken(ReglasDescuentoParser.T_SINO, 0)

        def T_SI(self):
            return self.getToken(ReglasDescuentoParser.T_SI, 0)

        def condicion(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.CondicionContext,0)


        def T_ENTONCES(self):
            return self.getToken(ReglasDescuentoParser.T_ENTONCES, 0)

        def accion(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.AccionContext,0)


        def resto(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.RestoContext,0)


        def getRuleIndex(self):
            return ReglasDescuentoParser.RULE_resto

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitResto" ):
                return visitor.visitResto(self)
            else:
                return visitor.visitChildren(self)




    def resto(self):

        localctx = ReglasDescuentoParser.RestoContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_resto)
        try:
            self.state = 47
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 37
                self.match(ReglasDescuentoParser.T_SINO)
                self.state = 38
                self.match(ReglasDescuentoParser.T_SI)
                self.state = 39
                self.condicion(0)
                self.state = 40
                self.match(ReglasDescuentoParser.T_ENTONCES)
                self.state = 41
                self.accion()
                self.state = 42
                self.resto()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 44
                self.match(ReglasDescuentoParser.T_SINO)
                self.state = 45
                self.accion()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CondicionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def termino(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.TerminoContext,0)


        def condicion(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.CondicionContext,0)


        def T_OR(self):
            return self.getToken(ReglasDescuentoParser.T_OR, 0)

        def getRuleIndex(self):
            return ReglasDescuentoParser.RULE_condicion

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCondicion" ):
                return visitor.visitCondicion(self)
            else:
                return visitor.visitChildren(self)



    def condicion(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = ReglasDescuentoParser.CondicionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 8
        self.enterRecursionRule(localctx, 8, self.RULE_condicion, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 50
            self.termino(0)
            self._ctx.stop = self._input.LT(-1)
            self.state = 57
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,2,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = ReglasDescuentoParser.CondicionContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_condicion)
                    self.state = 52
                    if not self.precpred(self._ctx, 2):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                    self.state = 53
                    self.match(ReglasDescuentoParser.T_OR)
                    self.state = 54
                    self.termino(0) 
                self.state = 59
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,2,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class TerminoContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def factor(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.FactorContext,0)


        def termino(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.TerminoContext,0)


        def T_AND(self):
            return self.getToken(ReglasDescuentoParser.T_AND, 0)

        def getRuleIndex(self):
            return ReglasDescuentoParser.RULE_termino

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTermino" ):
                return visitor.visitTermino(self)
            else:
                return visitor.visitChildren(self)



    def termino(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = ReglasDescuentoParser.TerminoContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 10
        self.enterRecursionRule(localctx, 10, self.RULE_termino, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 61
            self.factor()
            self._ctx.stop = self._input.LT(-1)
            self.state = 68
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = ReglasDescuentoParser.TerminoContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_termino)
                    self.state = 63
                    if not self.precpred(self._ctx, 2):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                    self.state = 64
                    self.match(ReglasDescuentoParser.T_AND)
                    self.state = 65
                    self.factor() 
                self.state = 70
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class FactorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def T_NOT(self):
            return self.getToken(ReglasDescuentoParser.T_NOT, 0)

        def factor(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.FactorContext,0)


        def T_PARI(self):
            return self.getToken(ReglasDescuentoParser.T_PARI, 0)

        def condicion(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.CondicionContext,0)


        def T_PARD(self):
            return self.getToken(ReglasDescuentoParser.T_PARD, 0)

        def comparacion(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.ComparacionContext,0)


        def funcion_tiempo(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.Funcion_tiempoContext,0)


        def getRuleIndex(self):
            return ReglasDescuentoParser.RULE_factor

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFactor" ):
                return visitor.visitFactor(self)
            else:
                return visitor.visitChildren(self)




    def factor(self):

        localctx = ReglasDescuentoParser.FactorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_factor)
        try:
            self.state = 79
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [8]:
                self.enterOuterAlt(localctx, 1)
                self.state = 71
                self.match(ReglasDescuentoParser.T_NOT)
                self.state = 72
                self.factor()
                pass
            elif token in [16]:
                self.enterOuterAlt(localctx, 2)
                self.state = 73
                self.match(ReglasDescuentoParser.T_PARI)
                self.state = 74
                self.condicion(0)
                self.state = 75
                self.match(ReglasDescuentoParser.T_PARD)
                pass
            elif token in [9]:
                self.enterOuterAlt(localctx, 3)
                self.state = 77
                self.comparacion()
                pass
            elif token in [10]:
                self.enterOuterAlt(localctx, 4)
                self.state = 78
                self.funcion_tiempo()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ComparacionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def atributo(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.AtributoContext,0)


        def T_RELOP(self):
            return self.getToken(ReglasDescuentoParser.T_RELOP, 0)

        def operando(self):
            return self.getTypedRuleContext(ReglasDescuentoParser.OperandoContext,0)


        def getRuleIndex(self):
            return ReglasDescuentoParser.RULE_comparacion

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitComparacion" ):
                return visitor.visitComparacion(self)
            else:
                return visitor.visitChildren(self)




    def comparacion(self):

        localctx = ReglasDescuentoParser.ComparacionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_comparacion)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 81
            self.atributo()
            self.state = 82
            self.match(ReglasDescuentoParser.T_RELOP)
            self.state = 83
            self.operando()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AtributoContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def T_OBJETO(self):
            return self.getToken(ReglasDescuentoParser.T_OBJETO, 0)

        def T_PUNTO(self):
            return self.getToken(ReglasDescuentoParser.T_PUNTO, 0)

        def T_ID(self):
            return self.getToken(ReglasDescuentoParser.T_ID, 0)

        def getRuleIndex(self):
            return ReglasDescuentoParser.RULE_atributo

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAtributo" ):
                return visitor.visitAtributo(self)
            else:
                return visitor.visitChildren(self)




    def atributo(self):

        localctx = ReglasDescuentoParser.AtributoContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_atributo)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 85
            self.match(ReglasDescuentoParser.T_OBJETO)
            self.state = 86
            self.match(ReglasDescuentoParser.T_PUNTO)
            self.state = 87
            self.match(ReglasDescuentoParser.T_ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Funcion_tiempoContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def T_TIEMPO(self):
            return self.getToken(ReglasDescuentoParser.T_TIEMPO, 0)

        def T_PARI(self):
            return self.getToken(ReglasDescuentoParser.T_PARI, 0)

        def T_ID(self):
            return self.getToken(ReglasDescuentoParser.T_ID, 0)

        def T_PARD(self):
            return self.getToken(ReglasDescuentoParser.T_PARD, 0)

        def getRuleIndex(self):
            return ReglasDescuentoParser.RULE_funcion_tiempo

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFuncion_tiempo" ):
                return visitor.visitFuncion_tiempo(self)
            else:
                return visitor.visitChildren(self)




    def funcion_tiempo(self):

        localctx = ReglasDescuentoParser.Funcion_tiempoContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_funcion_tiempo)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 89
            self.match(ReglasDescuentoParser.T_TIEMPO)
            self.state = 90
            self.match(ReglasDescuentoParser.T_PARI)
            self.state = 91
            self.match(ReglasDescuentoParser.T_ID)
            self.state = 92
            self.match(ReglasDescuentoParser.T_PARD)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OperandoContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def T_ID(self):
            return self.getToken(ReglasDescuentoParser.T_ID, 0)

        def T_NUM(self):
            return self.getToken(ReglasDescuentoParser.T_NUM, 0)

        def T_PORCENTAJE(self):
            return self.getToken(ReglasDescuentoParser.T_PORCENTAJE, 0)

        def getRuleIndex(self):
            return ReglasDescuentoParser.RULE_operando

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOperando" ):
                return visitor.visitOperando(self)
            else:
                return visitor.visitChildren(self)




    def operando(self):

        localctx = ReglasDescuentoParser.OperandoContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_operando)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 94
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 14336) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AccionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def T_APLICAR(self):
            return self.getToken(ReglasDescuentoParser.T_APLICAR, 0)

        def T_DESCUENTO(self):
            return self.getToken(ReglasDescuentoParser.T_DESCUENTO, 0)

        def T_PARI(self):
            return self.getToken(ReglasDescuentoParser.T_PARI, 0)

        def T_PORCENTAJE(self):
            return self.getToken(ReglasDescuentoParser.T_PORCENTAJE, 0)

        def T_PARD(self):
            return self.getToken(ReglasDescuentoParser.T_PARD, 0)

        def getRuleIndex(self):
            return ReglasDescuentoParser.RULE_accion

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAccion" ):
                return visitor.visitAccion(self)
            else:
                return visitor.visitChildren(self)




    def accion(self):

        localctx = ReglasDescuentoParser.AccionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_accion)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 96
            self.match(ReglasDescuentoParser.T_APLICAR)
            self.state = 97
            self.match(ReglasDescuentoParser.T_DESCUENTO)
            self.state = 98
            self.match(ReglasDescuentoParser.T_PARI)
            self.state = 99
            self.match(ReglasDescuentoParser.T_PORCENTAJE)
            self.state = 100
            self.match(ReglasDescuentoParser.T_PARD)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[4] = self.condicion_sempred
        self._predicates[5] = self.termino_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def condicion_sempred(self, localctx:CondicionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 2)
         

    def termino_sempred(self, localctx:TerminoContext, predIndex:int):
            if predIndex == 1:
                return self.precpred(self._ctx, 2)
         




