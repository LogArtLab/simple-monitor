from antlr4 import InputStream, CommonTokenStream

from simplemonitor.stl import Semantics
from simplemonitor.stl.STLLexer import STLLexer
from simplemonitor.stl.STLParser import STLParser


class OfflineMonitor:

    def __init__(self, prog_context: STLParser.ProgContext):
        self.prog_context = prog_context

    def monitor(self, semantics: Semantics):
        return semantics.visit(self.prog_context)


class STLOfflineMonitorBuilder:

    def __init__(self, formula):
        self.formula = formula

    def build(self) -> OfflineMonitor:
        expr = InputStream(self.formula + '\n')
        lexer = STLLexer(input=expr)
        token_stream = CommonTokenStream(lexer)
        parser = STLParser(token_stream)
        return OfflineMonitor(parser.prog())


class OnlineMonitor:

    def __init__(self, prog_context: STLParser.ProgContext):
        self.prog_context = prog_context

    def monitor(self, semantics: Semantics):
        return semantics.visit(self.prog_context)