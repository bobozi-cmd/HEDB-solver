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


class OpLog:
    def __init__(
        self, dtype:str, op: str, vars: tuple["z3.ArithRef"], result: "z3.ArithRef"
    ) -> None:
        self.dtype = dtype
        self.op = op  # plaintext, [+,-,*,/,%,^,SUM,AVG,MAX,MIN,>,<,==,<=,>=,!=]
        self.vars = vars  # tuple of z3.ArithRef
        self.result = result  # z3.ArithRef or True or False

    def __repr__(self) -> str:
        s = f"{self.dtype}({self.op}"
        for v in self.vars:
            s += f" {v}"
        s += f") -> {self.result}"
        return s


if __name__ == "__main__":
    print(f"op length is {len(ops)}, compare ops index is {cmp_ops_idx}, length is {cmp_ops_len}")