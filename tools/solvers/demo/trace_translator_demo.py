import z3


class TraceTranslator():

    def __init__(self, file: str) -> None:
        self.file = file
        with open(file, 'r') as fp:
            self.contents = fp.readlines()
        self.vars_table: dict[str, z3.ArithRef] = {}
        self.formulas = []

    def check_and_add(self, var: str):
        if var not in self.vars_table:
            self.vars_table[var] = z3.Int(var)
    
    def parse_unary_formula(self, toks: list) -> str:
        self.check_and_add(toks[0])
        return f"self.vars_table['{toks[0]}'] {toks[1]} {toks[2]}"

    def parser_binary_formula(self, toks: list[str]) -> str:
        formula = ""
        for tok in toks:
            if (tok not in ['(', ')', '+', '-', '*', '/', '==']) and (not tok.isdigit()):
                self.check_and_add(tok)
                formula += f"self.vars_table['{tok}']"
            else:
                formula += tok
        return formula

    def parse(self):
        for line in self.contents:
            filter_line = line.split("//")[0].strip()
            if filter_line == "":
                continue
            toks = filter_line.split(" ")
            if len(toks) == 3:
                formula = self.parse_unary_formula(toks)
            elif len(toks) == 7:
                formula = self.parser_binary_formula(toks)
            
            self.formulas.append(eval(formula))


if __name__ == "__main__":
    import argparse, time

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Path of file", type=str, required=True)
    args = parser.parse_args()

    tt = TraceTranslator(args.file)
    tt.parse()

    solver = z3.Solver()
    solver.add(tt.formulas)

    st = time.time_ns()
    ret = solver.check()
    et = time.time_ns()
    print(f"{ret}: {(et - st)/1000/1000:.4f}")

    