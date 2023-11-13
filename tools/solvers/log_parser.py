import pathlib
import pickle
import z3

from op_log import OpLog
from db_utils import create_z3_obj, Singleton


class LogParser:
    def __init__(self, file: "pathlib.Path") -> None:
        self.file = file
        self.variable_table: dict[str, "z3.ArithRef"] = {}
        self.r_variable_table: dict["z3.ArithRef", str] = {}
        self.op_logs: list["OpLog"] = []
        self._idx = 0

    def get_all(self) -> list["OpLog"]:
        """Get all op logs from log file"""
        with open(self.file, "r") as fp:
            for line in fp.readlines():
                line = line.strip()
                if not line:
                    continue
                self.op_logs.append(self.transform(line))
        return self.op_logs

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
        i(+ i_x0 i_x1) -> i_x2
        >>> lp.transform('i * 3 2 4 24')
        i(* i_x0 i_x3 i_x4) -> i_x5
        >>> lp.transform('f > 3.1 2.1 True')
        f(> f_x6 f_x7) -> True
        """
        toks = line.split()
        data_type = toks[0]
        op = toks[1]

        vars = []
        for v in toks[2:-1] if toks[-1] in ["True", "False"] else toks[2:]:
            if v not in self.variable_table:
                tmp = create_z3_obj(name=f"{data_type}_x{self._idx}", type=data_type)
                self._idx += 1
                self.variable_table[v] = tmp
                self.r_variable_table[tmp] = v
            else:
                tmp = self.variable_table[v]
            vars.append(tmp)

        res = toks[-1] if toks[-1] in ["True", "False"] else vars.pop(-1)
        return OpLog(dtype=data_type, op=op, vars=vars, result=res)

    def statistics(self) -> dict[str, int]:
        op_frequency = {}
        for log in self.op_logs:
            if log.op in op_frequency:
                op_frequency[log.op] += 1
            else:
                op_frequency[log.op] = 1
        return op_frequency


class LogParserSerialize(Singleton):
    """
    >>> LogParserSerialize().serialize(LogParser('./tmp'), './picktmp.pkl')
    >>> lp = LogParserSerialize().deserialize('./picktmp.pkl')
    >>> type(lp) == LogParser
    True
    >>> lp.file
    './tmp'
    """

    def serialize(self, obj: "LogParser", file_name: str):
        with open(file_name, "wb") as fp:
            pickle.dump(obj=obj, file=fp)

    def deserialize(self, file_name: str) -> "LogParser":
        with open(file_name, "rb") as fp:
            return pickle.load(file=fp)

LPS = LogParserSerialize()

