from typing import Any
import psycopg2, logging, datetime, z3, pathlib, subprocess

logging.basicConfig(
    filename=f'solver_{datetime.datetime.today().strftime("%Y_%m_%d")}.log',
    level=logging.DEBUG,
    format="[%(asctime)s] - [%(levelname)s] - %(funcName)s - %(message)s",
    datefmt="%Y-%m-%d-%H:%M:%S",
)


class Singleton:
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __New__(self, *args: Any, **kwds: Any):
        if self.__instance is None:
            self.__instance = super().__new__(*args, **kwds)
        return self.__instance


class DataType(Singleton):
    """
    >>> id(DataType()) == id(DataType())
    True
    """

    int_type = "i"
    float_type = "f"
    str_type = "s"
    timestamp_type = "s"

    data_types = {
        int_type: "enc_int4_decrypt",
        float_type: "enc_float4_decrypt",
        str_type: "enc_text_decrypt",
        timestamp_type: "enc_timestamp_decrypt",
    }


DT = DataType()

link_con = lambda: psycopg2.connect(
    database="secure_test",
    user="postgres",
    password="postgres",
    host="127.0.0.1",
    port="5432",
)


def query(con: "psycopg2.connection", sql: str):
    ret = None
    try:
        with con.cursor() as cur:
            cur.execute(sql)
            ret = cur.fetchall()
    except Exception as e:
        logging.error(f"Sql encounter error: {sql}")
    finally:
        return ret


def oracle(con: "psycopg2.connection", enc_var: str, data_type: str) -> str:
    if enc_var.lower() in ["true", "false"]:
        return enc_var
    sql = f"SELECT {DT.data_types[data_type]}('{enc_var}');"
    ret = query(con, sql)
    if ret is None:
        exit(-1)
    return ret[0][0]


def finishable_cmd(cmd: str):
    p = subprocess.Popen(cmd, shell=True, encoding="utf-8")
    p.wait()
    return p.returncode


class TraceGen:
    def __init__(
        self,
        link_con,
        log_dir: str,
        trace_dir: str,
    ) -> None:
        self.link_con = link_con
        self.log_dir = pathlib.Path(log_dir)
        self.trace_dir = pathlib.Path(trace_dir)
        self.tmp_path = pathlib.Path("/tmp/integrity_zone.log")
        # check path valid
        if not self.log_dir.exists():
            print(f"{self.log_dir} not exist")
            exit(-1)
        if not self.trace_dir.exists():
            self.trace_dir.mkdir()
            if not self.trace_dir.exists():
                print(f"{self.trace_dir} create failed")
                exit(-1)
        else:
            # clear all file in trace directory
            cmd = f"rm {self.trace_dir}/*.log"
            finishable_cmd(cmd)

    def generate_all(self):
        for file in self.log_dir.iterdir():
            if file.is_file() and file.name.endswith(".sql"):
                name = file.name.split("/")[-1].split(".sql")[0]
                self.get_trace(file, self.trace_dir.joinpath(f"{name}.log"))

    def get_trace(self, log_file: "pathlib.Path", trace_file: "pathlib.Path"):
        with open(log_file, "r") as fp:
            sql = " ".join(fp.readlines())
            ret = query(self.link_con(), sql=sql)

        cmd = f"sudo chmod 777 {self.tmp_path}; sudo mv {self.tmp_path} {trace_file}"
        if (retcode := finishable_cmd(cmd)) != 0:
            print(f"get_trace error: {cmd}! return code is {retcode}")


def create_z3_obj(name: str, type: str) -> z3.ArithRef:
    """create z3 object according to type

    >>> import z3
    >>> create_z3_obj('i0', 'i')
    i0
    >>> create_z3_obj('f0', 'f')
    f0
    >>> create_z3_obj('s0', 's')
    s0
    >>> create_z3_obj('nothing', 'no_type') == None
    True
    """
    match type:
        case DT.int_type:
            return z3.Int(name)
        case DT.float_type:
            return z3.Real(name)
        case DT.str_type | DT.timestamp_type:
            return z3.String(name)
        case other:
            logging.error(f"No type named: {other}")
            return None
