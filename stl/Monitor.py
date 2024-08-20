from antlr4 import InputStream, CommonTokenStream

from stl import Semantics
from stl.STLLexer import STLLexer
from stl.STLParser import STLParser


class Monitor:

    def __init__(self, prog_context: STLParser.ProgContext):
        self.prog_context = prog_context

    def monitor(self, semantics: Semantics):
        return semantics.visit(self.prog_context)


class STLMonitorBuilder:

    def __init__(self, formula):
        self.formula = formula

    def build(self) -> Monitor:
        expr = InputStream(self.formula + '\n')
        lexer = STLLexer(input=expr)
        token_stream = CommonTokenStream(lexer)
        parser = STLParser(token_stream)
        return Monitor(parser.prog())
