from base import *
from context import Context
from log_parser import LogParser
from log_checker import LogChecker
import signal


def handler(signum: "signal._SIGNUM", frame):
    if signal.SIGINT == signum:
        print("Goodbye!")
        exit(0)

def main():
    signal.signal(signal.SIGINT, handler=handler)

    global_ctx = Context()
    lp = LogParser("./trace/integrity_zone_min.log", global_ctx)
    lp.parser()
    
    lc = LogChecker(global_ctx)
    lc.analyze_all()

if __name__ == "__main__":
    main()
