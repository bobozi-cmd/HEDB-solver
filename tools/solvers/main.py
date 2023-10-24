import argparse, logging, datetime, signal, pathlib

from log_parser import LogParser

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


def run(log_file: str):
    log_path = pathlib.Path(log_file)
    if not log_path.exists():
        logging.error(f"{log_path} does not exist!")
        exit(-1) 
    # 1. parser file line-wise and generate op log
    log_parser = LogParser(file=log_path)
    logs = log_parser.get_all()
    logging.info(f"Logs length is {len(logs)}")
    for l in logs:
        print(l)
        input("next>")
    # 2. check new op log whether leak secret
    ...


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log", help="Path of log", type=str, required=True)
    args = parser.parse_args()

    logging.debug(f"Log path: {args.log}")

    signal.signal(signal.SIGINT, handler=handler)

    run(args.log)


if __name__ == "__main__":
    main()