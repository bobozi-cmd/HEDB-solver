from base import OpLog
import z3
class Context:
    def __init__(self) -> None:
        self.var_tb: dict = {}
        self.rvar_tb: dict = {}
        self.op_logs: list["OpLog"] = []
        self._idx = 0
        # cache
        self.pass_logs = []
        self.forbidden_logs = []

        self.solver = z3.Solver()