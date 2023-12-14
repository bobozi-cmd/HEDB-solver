from base import *
import z3
from context import Context

class LogChecker:

    def __init__(self, ctx: "Context") -> None:
        self.ctx = ctx

    def analyze_all(self):
        for log in self.ctx.op_logs:
            if self.analyze(log):
                self.ctx.pass_logs.append(log)
            else:
                HeLog.warning(f"analyze result: Secret exposed!")
                HeLog.debug(f"Now : {len(self.ctx.solver)}")
                self.ctx.forbidden_logs.append(log)
            # input("next>")
    
    def analyze(self, input_log: "OpLog") -> bool:
        if input_log in self.ctx.pass_logs:
            return True
        if input_log in self.ctx.forbidden_logs:
            return False

        need_check = set()
        candidate = set(input_log.vars)
        if input_log.op in ARITH_OPS:
            candidate.add(input_log.result)
        need_check.update(candidate)
        HeLog.debug(f"candidate: {candidate}")

        solver = self.ctx.solver
        ret = True
        # TODO: timeout function
        solver.push()
        solver.add(input_log.formula)
        for var in need_check:
            solver.push()
            solver.add(var != self.ctx.rvar_tb[var])
            if solver.check() != z3.sat:
                ret = False
                solver.pop()
                break
            solver.pop()
        solver.pop()

        if ret == True:
            solver.add(input_log.formula)
        return ret