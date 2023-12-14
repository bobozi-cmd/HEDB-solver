import z3

# Note: Assume only has int and float value

ARITH_OPS = ["+", "-", "*", "/", "%", "^", "SUM", "AVG"]
CMP_OPS = [">", "<", "==", "<=", ">=", "!=", "MAX", "MIN"]


class OpLog:
    def __init__(
        self, dtype: str, op: str, vars: list, result: z3.ArithRef | str
    ) -> None:
        pass


class OpLogFactory:
    """
    >>> from z3 import *
    >>> a, b, c = Ints("A B C")
    >>> op1 = OpLogFactory.create_op_log('i', '+', [a, b, 10], 10)
    >>> op2 = OpLogFactory.create_op_log('i', '>', [b, c], 'True')
    >>> type(op1) is ArithOpLog
    True
    >>> type(op2) is CmpOpLog
    True
    >>> op1
    A + B + 10 == 10
    >>> op2
    B > C
    >>> vars = [a, b, c]
    >>> op3 = OpLogFactory.create_op_log('i', 'SUM', [vars[0], vars[2], b, 10], 15)
    >>> op3
    A + C + B + 10 == 15
    """
    @classmethod
    def create_op_log(
        cls,
        dtype: str,
        op: str,
        vars: list,
        result: z3.ArithRef | str | int | float,
    ) -> "OpLog":
        # TODO: MAX and MIN's result is what
        if op in ARITH_OPS:
            return ArithOpLog(
                dtype=dtype,
                op="+" if op in ["SUM", "AVG"] else op,
                vars=vars,
                result=result,
            )
        elif op in CMP_OPS[:-2]:
            return CmpOpLog(dtype=dtype, op=op, vars=vars, result=result)


class ArithOpLog(OpLog):
    """
    >>> from z3 import *
    >>> a, b, c, d, e, f, g = Ints("a b c d e f g")
    >>> op1 = ArithOpLog('i', '+', [a, b], 10)
    >>> op2 = ArithOpLog('i', '-', [b, c, d, 5], f)
    >>> op1.formula
    a + b == 10
    >>> op2
    b - c - d - 5 == f
    """

    def __init__(
        self,
        dtype: str,
        op: str,
        vars: list["z3.ArithRef", int, float],  # Note: Assume no Nest logs
        result: z3.ArithRef,
    ):
        self.dtype = dtype
        self.op = op
        self.vars = vars
        self.result = result

        self.formula = self.generate_formula()

    def generate_formula(self) -> "z3.ArithRef":
        tmp = self.vars[0]
        for v in self.vars[1:]:
            tmp = eval(f"tmp {self.op} v")
        return tmp == self.result

    def __repr__(self) -> str:
        return str(self.formula)


class CmpOpLog(OpLog):
    """
    >>> from z3 import *
    >>> a, b, c, d = Ints("a b c d")
    >>> op1 = CmpOpLog('i', '>=', [a, b], 'True')
    >>> op2 = CmpOpLog('i', '>=', [c, d], 'False')
    >>> op3 = CmpOpLog('i', '>=', [12, d], 'False')
    >>> op1.formula
    a >= b
    >>> op2
    Not(c >= d)
    >>> op3.formula
    Not(d <= 12)
    >>> str(op3) == 'Not(d <= 12)'
    True
    """
    def __init__(
        self,
        dtype: str,
        op: str,
        vars: list["z3.ArithRef", int, float],  # Note: cmp op has only 2 vars
        result: z3.ArithRef,
    ):
        self.dtype = dtype
        self.op = op
        self.vars = vars
        self.result = result.lower()

        self.formula = self.generate_formula()

    def generate_formula(self) -> "z3.BoolRef":
        lval, rval = self.vars[0], self.vars[1]
        if self.result == "true":
            tmp = eval(f"lval {self.op} rval")
        elif self.result == "false":
            tmp = z3.Not(eval(f"lval {self.op} rval"))
        return tmp

    def __repr__(self) -> str:
        return str(self.formula)