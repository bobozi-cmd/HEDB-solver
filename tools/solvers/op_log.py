import z3

ops = [
    "+",
    "-",
    "*",
    "/",
    "%",
    "^",
    "SUM",
    "AVG",
    "MAX",
    "MIN",
    # compare operations field
    ">",
    "<",
    "==",
    "<=",
    ">=",
    "!=",
]
cmp_ops_idx = ops.index(">")
cmp_ops_len = 6


class LeftOp:
    def __init__(
        self, dtype: str, op: str, vars: list["z3.ArithRef", "LeftOp"]
    ) -> None:
        self.dtype = dtype
        self.op = op  # plaintext, [+,-,*,/,%,^,SUM,AVG,MAX,MIN,>,<,==,<=,>=,!=]
        self.vars = vars  # list of z3.ArithRef

    def __repr__(self) -> str:
        s = f"{self.dtype}({self.op}"
        for v in self.vars:
            s += f" {v}"
        s += f")"
        return s

    def search_and_replace(self, target: "z3.ArithRef", substitute: "LeftOp"):
        """
        >>> v1 = LeftOp('i', '+', ['a', 'b'])
        >>> v2 = LeftOp('i', '*', ['a', 'c'])
        >>> v2.search_and_replace('c', v1)
        >>> v2
        i(* a i(+ a b))
        >>> v3 = LeftOp('i', '-', ['x', 'y', 'z'])
        >>> v2.search_and_replace('a', v3)
        >>> v2
        i(* i(- x y z) i(+ i(- x y z) b))
        """
        for i in range(len(self.vars)):
            if type(self.vars[i]) == LeftOp:
                self.vars[i].search_and_replace(target, substitute)
            else:
                if self.vars[i] == target:
                    self.vars[i] = substitute


class OpLog:
    def __init__(
        self,
        dtype: str,
        op: str,
        vars: list["z3.ArithRef"] | LeftOp,
        result: "z3.ArithRef",
    ) -> None:
        self.left_op = vars if type(vars) == LeftOp else LeftOp(dtype, op, vars)
        self.result = result  # z3.ArithRef or True or False

    def __repr__(self) -> str:
        s = f"{self.left_op} -> {self.result}"
        return s

    @property
    def op(self):
        return self.left_op.op

    @property
    def dtype(self):
        return self.left_op.dtype

    @property
    def vars(self):
        return self.left_op.vars

    def search_and_replace(self, other_op: "OpLog"):
        if type(other_op.result) is z3.ArithRef:
            self.left_op.search_and_replace(other_op.result, other_op.left_op)


if __name__ == "__main__":
    print(
        f"op length is {len(ops)}, compare ops index is {cmp_ops_idx}, length is {cmp_ops_len}"
    )
