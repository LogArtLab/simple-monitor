# Generated from MITL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .MITLParser import MITLParser
else:
    from MITLParser import MITLParser

# This class defines a complete generic visitor for a parse tree produced by MITLParser.

class MITLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by MITLParser#prog.
    def visitProg(self, ctx:MITLParser.ProgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MITLParser#Not.
    def visitNot(self, ctx:MITLParser.NotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MITLParser#AndOrImpl.
    def visitAndOrImpl(self, ctx:MITLParser.AndOrImplContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MITLParser#U.
    def visitU(self, ctx:MITLParser.UContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MITLParser#F.
    def visitF(self, ctx:MITLParser.FContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MITLParser#parensFormula.
    def visitParensFormula(self, ctx:MITLParser.ParensFormulaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MITLParser#trueFalse.
    def visitTrueFalse(self, ctx:MITLParser.TrueFalseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MITLParser#G.
    def visitG(self, ctx:MITLParser.GContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MITLParser#Atom.
    def visitAtom(self, ctx:MITLParser.AtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MITLParser#interval.
    def visitInterval(self, ctx:MITLParser.IntervalContext):
        return self.visitChildren(ctx)



del MITLParser