from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream

from simplemonitor.mitl.MITLLexer import MITLLexer
from simplemonitor.mitl.MITLParser import MITLParser
from simplemonitor.mitl.MITLVisitor import MITLVisitor

class Semantics(MITLVisitor):
    def __init__(self, trace = None, current_event=0):
        self.trace = trace
        self.current_event = current_event

    def get_event_time(self,index):
        return self.trace[index][0]

    def get_event_state(self,index):
        return self.trace[index][1]

    def get_current_event_state(self):
        return self.get_event_state(self.current_event)

    def get_current_event_time(self):
        return self.get_event_time(self.current_event)

    def compute_interval(self,ctx_interval):
        return float(str(ctx_interval.NUMBER(0))),float(str(ctx_interval.NUMBER(1)))

    def visitParensFormula(self, ctx: MITLParser.ParensFormulaContext):
        return self.visit(ctx.formula())


class BooleanSemantics(Semantics):

    def __init__(self, trace=None, current_event=0):
        super().__init__(trace, current_event)

    def visitNot(self, ctx: MITLParser.NotContext):
        return not self.visit(ctx.formula())

    def visitAndOrImpl(self, ctx: MITLParser.AndOrImplContext):
        left_formula = self.visit(ctx.formula(0))
        right_formula = self.visit(ctx.formula(1))
        if ctx.op.type == MITLParser.AND:
            return left_formula and  right_formula
        if ctx.op.type == MITLParser.OR:
            return left_formula or right_formula
        if  ctx.op.type == MITLParser.IMPL:
            return not left_formula or right_formula

    def visitU(self, ctx: MITLParser.UContext):
        t0, t1 = self.compute_interval(ctx.interval())
        actualized_t0 = t0 + self.get_current_event_time()
        actualized_t1 = t1 + self.get_current_event_time()
        left_formula = ctx.formula(0)
        right_formula = ctx.formula(1)
        for i in range(self.current_event, len(self.trace)):
            if self.get_event_time(i)<actualized_t0:
                if not BooleanSemantics(trace=self.trace,current_event=i).visit(left_formula):
                    return False
            if actualized_t0<=self.get_event_time(i)<=actualized_t1:
                if not BooleanSemantics(trace=self.trace,current_event=i).visit(left_formula):
                    return False
                elif BooleanSemantics(trace=self.trace,current_event=i).visit(right_formula):
                    return True
            if self.get_event_time(i)>actualized_t1:
                return False
        return False

    def visitF(self, ctx: MITLParser.FContext):
        t0,t1 = self.compute_interval(ctx.interval())
        actualized_t0 = t0 + self.get_current_event_time()
        actualized_t1 = t1 + self.get_current_event_time()
        for i in range(self.current_event,len(self.trace)):
            if actualized_t0<=self.get_event_time(i)<=actualized_t1:
                if BooleanSemantics(trace=self.trace,current_event=i).visit(ctx.formula()):
                    return True
            if self.get_event_time(i)>actualized_t1:
                return False
        return False

    def visitTrueFalse(self, ctx: MITLParser.TrueFalseContext):
        if ctx.op.type == MITLParser.TRUE:
            return True
        elif ctx.op.type == MITLParser.FALSE:
            return False

    def visitG(self, ctx: MITLParser.GContext):
        t0, t1 = self.compute_interval(ctx.interval())
        actualized_t0 = t0 + self.get_current_event_time()
        actualized_t1 = t1 + self.get_current_event_time()
        for i in range(self.current_event, len(self.trace)):
            if actualized_t0 <= self.get_event_time(i) <= actualized_t1:
                if not BooleanSemantics(trace=self.trace, current_event=i).visit(ctx.formula()):
                    return False
            if self.get_event_time(i) > actualized_t1:
                return True
        return True

    def visitAtom(self, ctx: MITLParser.AtomContext):
        return str(ctx.PARAMETERS()) in self.get_current_event_state()


def time_robustness(left_time, right_time, time):
    if time <= left_time:
        return time - left_time
    if time>=right_time:
        return right_time - time
    return min(time-left_time,right_time-time)

class TimeRobustnessSemantics(Semantics):

    def __init__(self, trace=None, current_event=0):
        super().__init__(trace, current_event)

    def visitNot(self, ctx: MITLParser.NotContext):
        return - self.visit(ctx.formula())

    def visitAndOrImpl(self, ctx: MITLParser.AndOrImplContext):
        left_formula = self.visit(ctx.formula(0))
        right_formula = self.visit(ctx.formula(1))
        if ctx.op.type == MITLParser.AND:
            return min(left_formula,right_formula)
        if ctx.op.type == MITLParser.OR:
            return max(left_formula,right_formula)
        if  ctx.op.type == MITLParser.IMPL:
            return max(-left_formula,right_formula)

    def visitU(self, ctx: MITLParser.UContext):
        rob = -float("inf")
        rob_inner = float("inf")
        t0, t1 = self.compute_interval(ctx.interval())
        actualized_t0 = t0 + self.get_current_event_time()
        actualized_t1 = t1 + self.get_current_event_time()
        left_formula = ctx.formula(0)
        right_formula = ctx.formula(1)
        for i in range(self.current_event, len(self.trace)-1):
            rob_inner = min(rob_inner,TimeRobustnessSemantics(trace=self.trace, current_event=i).visit(left_formula))
            rob = max(rob,min(rob_inner,min(TimeRobustnessSemantics(trace=self.trace, current_event=i+1).visit(right_formula),
                                            time_robustness(actualized_t0, actualized_t1, self.get_event_time(i+1)))))
        return rob

    def visitF(self, ctx: MITLParser.FContext):
        rob = -float("inf")
        t0,t1 = self.compute_interval(ctx.interval())
        actualized_t0 = t0 + self.get_current_event_time()
        actualized_t1 = t1 + self.get_current_event_time()
        for i in range(self.current_event,len(self.trace)):
            actual_time_robustness = time_robustness(actualized_t0, actualized_t1, self.get_event_time(i))
            rob = max(rob,min(TimeRobustnessSemantics(trace=self.trace,current_event=i).visit(ctx.formula()),actual_time_robustness))
        return rob

    def visitTrueFalse(self, ctx: MITLParser.TrueFalseContext):
        if ctx.op.type == MITLParser.TRUE:
            return float("inf")
        elif ctx.op.type == MITLParser.FALSE:
            return -float("inf")

    def visitG(self, ctx: MITLParser.GContext):
        rob = float("inf")
        t0, t1 = self.compute_interval(ctx.interval())
        actualized_t0 = t0 + self.get_current_event_time()
        actualized_t1 = t1 + self.get_current_event_time()
        for i in range(self.current_event, len(self.trace)):
            actual_time_robustness = time_robustness(actualized_t0, actualized_t1, self.get_event_time(i))
            rob = min(rob, max(TimeRobustnessSemantics(trace=self.trace, current_event=i).visit(ctx.formula()),
                               -actual_time_robustness))
        return rob

    def visitAtom(self, ctx: MITLParser.AtomContext):
        if str(ctx.PARAMETERS()) in self.get_current_event_state():
            return float("inf")
        else:
            return -float("inf")


#formula = "G[0,INF](p --> F[0,2] q)"
#formula = "F[1,5](F[0,10] q)"
# formula = "p U[10,15] q"
formula = "(F[1,2] p) & (F[4,5] q)"
expr = InputStream(formula)
lexer = MITLLexer(input=expr)
token_stream = CommonTokenStream(lexer)
parser = MITLParser(token_stream)
prog_context = parser.prog()

trace = [(0,{"q"}),(7, {"p"}),(12.5,{"q"})]
a = TimeRobustnessSemantics(trace =trace).visit(prog_context)
print(a)
