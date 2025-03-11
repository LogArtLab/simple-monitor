# Generated from MITL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .MITLParser import MITLParser
else:
    from MITLParser import MITLParser

# This class defines a complete listener for a parse tree produced by MITLParser.
class MITLListener(ParseTreeListener):

    # Enter a parse tree produced by MITLParser#prog.
    def enterProg(self, ctx:MITLParser.ProgContext):
        pass

    # Exit a parse tree produced by MITLParser#prog.
    def exitProg(self, ctx:MITLParser.ProgContext):
        pass


    # Enter a parse tree produced by MITLParser#Not.
    def enterNot(self, ctx:MITLParser.NotContext):
        pass

    # Exit a parse tree produced by MITLParser#Not.
    def exitNot(self, ctx:MITLParser.NotContext):
        pass


    # Enter a parse tree produced by MITLParser#AndOrImpl.
    def enterAndOrImpl(self, ctx:MITLParser.AndOrImplContext):
        pass

    # Exit a parse tree produced by MITLParser#AndOrImpl.
    def exitAndOrImpl(self, ctx:MITLParser.AndOrImplContext):
        pass


    # Enter a parse tree produced by MITLParser#U.
    def enterU(self, ctx:MITLParser.UContext):
        pass

    # Exit a parse tree produced by MITLParser#U.
    def exitU(self, ctx:MITLParser.UContext):
        pass


    # Enter a parse tree produced by MITLParser#F.
    def enterF(self, ctx:MITLParser.FContext):
        pass

    # Exit a parse tree produced by MITLParser#F.
    def exitF(self, ctx:MITLParser.FContext):
        pass


    # Enter a parse tree produced by MITLParser#parensFormula.
    def enterParensFormula(self, ctx:MITLParser.ParensFormulaContext):
        pass

    # Exit a parse tree produced by MITLParser#parensFormula.
    def exitParensFormula(self, ctx:MITLParser.ParensFormulaContext):
        pass


    # Enter a parse tree produced by MITLParser#trueFalse.
    def enterTrueFalse(self, ctx:MITLParser.TrueFalseContext):
        pass

    # Exit a parse tree produced by MITLParser#trueFalse.
    def exitTrueFalse(self, ctx:MITLParser.TrueFalseContext):
        pass


    # Enter a parse tree produced by MITLParser#G.
    def enterG(self, ctx:MITLParser.GContext):
        pass

    # Exit a parse tree produced by MITLParser#G.
    def exitG(self, ctx:MITLParser.GContext):
        pass


    # Enter a parse tree produced by MITLParser#Atom.
    def enterAtom(self, ctx:MITLParser.AtomContext):
        pass

    # Exit a parse tree produced by MITLParser#Atom.
    def exitAtom(self, ctx:MITLParser.AtomContext):
        pass


    # Enter a parse tree produced by MITLParser#interval.
    def enterInterval(self, ctx:MITLParser.IntervalContext):
        pass

    # Exit a parse tree produced by MITLParser#interval.
    def exitInterval(self, ctx:MITLParser.IntervalContext):
        pass



del MITLParser