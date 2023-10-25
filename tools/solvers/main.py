import argparse, logging, datetime, signal, pathlib

from log_parser import LogParser
from db_utils import link_con, TraceGen

logging.basicConfig(
    filename=f'solver_{datetime.datetime.today().strftime("%Y_%m_%d")}.log',
    level=logging.DEBUG,
    format="[%(asctime)s] - [%(levelname)s] - %(funcName)s - %(message)s",
    datefmt="%Y-%m-%d-%H:%M:%S",
)


def handler(signum: "signal._SIGNUM", frame):
    if signal.SIGINT == signum:
        print("Goodbye!")
        exit(0)


def gen_trace(sql_path: str, trace_path: str):
    tg = TraceGen(link_con=link_con, sql_dir=sql_path, trace_dir=trace_path)
    tg.generate_all()


def run(log_file: str):
    log_path = pathlib.Path(log_file)
    if not log_path.exists():
        logging.error(f"{log_path} does not exist!")
        exit(-1)
    # 1. parser file line-wise and generate op log
    lp = LogParser(file=log_path)
    lp.get_all()
    logging.info(f"Logs length is {len(lp.op_logs)}")
    print(lp.statistics())
    # 2. check new op log whether leak secret
    ...


def main():
    parser = argparse.ArgumentParser()

    subp = parser.add_subparsers(dest="cmd", required=True)
    trace = subp.add_parser("trace", help="Generate sql traces")
    trace.add_argument(
        "-q", "--sql", help="Path of sqls directory", type=str, required=True
    )
    trace.add_argument(
        "-t", "--trace", help="Path of trace directory", type=str, required=True
    )

    analysis = subp.add_parser("analysis", help="Analysis log file")
    analysis.add_argument("-l", "--log", help="Path of log", type=str, required=True)
    args = parser.parse_args()

    signal.signal(signal.SIGINT, handler=handler)

    if args.cmd == "trace":
        gen_trace(sql_path=args.sql, trace_path=args.trace)
    elif args.cmd == "analysis":
        run(log_file=args.log)


if __name__ == "__main__":
    main()
