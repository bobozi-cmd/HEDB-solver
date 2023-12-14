from context import Context
from base import *

class LogParser:

    def __init__(self, file, ctx: "Context"=Context()) -> None:
        self.file = file
        self.ctx = ctx
    
    def parser(self):
        """parser all logs in file"""
        with open(self.file, 'r') as fp:
            for line in fp.readlines():
                line = line.strip()
                if not line:
                    continue
                self.ctx.op_logs.append(self.transform(line))
    
    def transform(self, line: str) -> "OpLog":
        """Transform line into a OpLog
        log format: data_type op var1 ... varn res
            data_type:
                i: integer
                f: float
                s: string
            op: +,-,*,/,%,^,SUM,AVG,MAX,MIN,>,<,==,<=,>=,!=
            res: value, False, True

        >>> lp = LogParser(None)
        >>> lp.transform('i + 3 19 22')
        x0 + x1 == x2
        >>> lp.transform('i * 3 2 4 24')
        x0*x3*x4 == x5
        >>> lp.transform('f > 3.1 2.1 True')
        x6 > x7
        """
        toks = line.split()
        data_type = toks[0]
        op = toks[1]

        vars = []
        for v in toks[2:-1] if op in CMP_OPS else toks[2:]:
            if v not in self.ctx.var_tb:
                tmp = create_z3_obj(f"x{self.ctx._idx}", data_type)
                self.ctx._idx += 1
                self.ctx.var_tb[v] = tmp
                self.ctx.rvar_tb[tmp] = oracle(link_con(), v, data_type)
            else:
                tmp = self.ctx.var_tb[v]
            vars.append(tmp)
        
        res = toks[-1] if op in CMP_OPS else vars.pop(-1)
        return OpLogFactory.create_op_log(data_type, op, vars, res)