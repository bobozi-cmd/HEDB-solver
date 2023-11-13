import argparse, logging, datetime, signal
import time

import psycopg2
import z3

con: "psycopg2.connection" = psycopg2.connect(
    database='secure_test', 
    user='postgres', 
    password='postgres', 
    host='127.0.0.1', 
    port='5432'
)

variable_table: dict = {}
r_variable_table: dict = {}
logs: list = []
tag = 'x'
idx = 0

logging.basicConfig(
    filename=f'solver_{datetime.datetime.today().strftime("%Y_%m_%d")}.log',
    level=logging.DEBUG,
    format='[%(asctime)s] - [%(levelname)s] - %(funcName)s - %(message)s',
    datefmt = '%Y-%m-%d-%H:%M:%S'
)


def handler(signum: "signal._SIGNUM", frame):
    if signal.SIGINT == signum:
        print("Goodbye!")
        exit(0)


def oracle(enc_var: str) -> str:
    if enc_var.lower() in ["true", "false"]:
        return enc_var
    with con:
        cur = con.cursor()
        cur.execute(f"SELECT enc_int4_decrypt('{enc_var}');")
        ret = cur.fetchall()[0][0]
    return ret


class OpLog():

    def __init__(self, op: str, vars: tuple, result) -> None:
        self.op = op
        self.vars = vars
        self.result = result

    def __repr__(self) -> str:
        s = f"({self.op}"
        for v in self.vars:
            s += f" {v}"
        s += f") -> {self.result}"
        return s


def transform(raw_line: str):
    global idx
    # TODO: Change code to apply for new format
    # format: op var1 var2 result (old)
    # new format: [f/i/s] op var1 var2 ... res(val/True/False)
    #             op: [+,-,*,/,%,^,SUM,AVG,MAX,MIN,>,<,==,<=,>=,!=]
    tokens = raw_line.strip().split()
    op = tokens[0]
    
    vars = []
    for v in tokens[1:]:
        if v not in variable_table:
            # TODO: recognize type
            tmp = z3.Int(f"{tag}{idx}")
            idx = idx + 1
            variable_table[v] = tmp
            r_variable_table[tmp] = oracle(v)
        else:
            tmp = variable_table[v]
        vars.append(tmp)

    return OpLog(op, tuple(vars[:-1]), vars[-1])


def analyze(input_log: "OpLog"):

    need_check = set()
    candidate = set(input_log.vars)
    candidate.add(input_log.result)
    need_check.update(candidate)
    
    logging.debug(f"candidate: {candidate}")
    solver = z3.Solver()

    def check_op(log: "OpLog"):
        nonlocal solver
        if log.op == "+":
            # z3.Sum()
            solver.add(log.vars[0] + log.vars[1] == log.result)
        elif log.op == "-":
            # if log.vars[0] == log.vars[1]:
            #     solver.add(log.vars[0] - log.vars[1] == 0)
            # else:
            #     solver.add(log.vars[0] - log.vars[1] == log.result)
            solver.add(log.vars[0] - log.vars[1] == log.result)
        elif log.op == "/":
            solver.add(log.vars[0] / log.vars[1] == log.result)
            solver.add(log.vars[1] != 0)
        elif log.op == "*":
            solver.add(log.vars[0] * log.vars[1] == log.result)

    check_op(input_log)
    for log in logs:
        log_candidate = set(log.vars)
        log_candidate.add(log.result)

        if candidate.intersection(log_candidate):
            need_check.update(log_candidate)
            check_op(log)
    
    logging.debug(f"need check: {need_check}")

    for var in need_check:
        solver.push()
        solver.add(var != r_variable_table[var])
        if solver.check() == z3.CheckSatResult(z3.Z3_L_FALSE):
            logging.info(f"{solver}")
            return False
        logging.info(f"{solver}")
        logging.info(f"{solver.model()}")
        solver.pop()

    return True


def run(integrity_zone: str, privacy_zone: str):
    with open(integrity_zone, "r") as integrity_fp, open(privacy_zone, "r") as privacy_fp:
        while True:
            if not privacy_fp.readable():
                    continue
            line = privacy_fp.readline().strip()
            if line:
                logging.debug(f"raw: {line}")
                new_log = transform(line)
                logging.debug(f"transform: {new_log}")
                
                result = analyze(new_log)
                if not result:
                    logging.warning(f"analyze result: Secret exposed!")
                else:
                    logs.append(new_log)

            # time.sleep(1)
            input("next>")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--integrity", help="Path of intergrity.log", type=str, required=True)
    parser.add_argument("-p", "--privacy", help="Path of privacy.log", type=str, required=True)
    args = parser.parse_args()

    logging.debug(f"i: {args.integrity}, p: {args.privacy}")

    signal.signal(signal.SIGINT, handler=handler)

    run(args.integrity, args.privacy)
    

"""
(- 7 7) = 0
(/ 7 7) = 1
(/ 1 1) = 2
(* 2 2) = 4
(* 4 2) = 8
"""
if __name__ == "__main__":
    # CLIENT_ORDER = 0
    # SERVER_ORDER = 1

    # integrity_zone = "./integrity_zone.log"
    # privacy_zone = "./privacy_zone.log"

    # with open(integrity_zone, "r") as integrity_fp, open(privacy_zone, "r") as privacy_fp:
    #     current_id = 1
    #     order = CLIENT_ORDER
    #     line = None

    #     while True:
    #         while order == CLIENT_ORDER:
    #             if not privacy_fp.readable():
    #                 continue
    #             line = privacy_fp.readline().strip()
    #             if line:
    #                 order = SERVER_ORDER
    #                 print(log_line(line))

    #         input('')
    #         order = CLIENT_ORDER
    main()