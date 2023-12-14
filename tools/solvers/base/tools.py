import logging, datetime, psycopg2, subprocess, z3, traceback

logging.basicConfig(
    filename=f'solver_{datetime.datetime.today().strftime("%Y_%m_%d")}.log',
    level=logging.DEBUG,
    format='[%(asctime)s] - [%(levelname)s] - %(funcName)s - %(message)s',
    datefmt = '%Y-%m-%d-%H:%M:%S'
)

HeLog = logging.getLogger()

class Singleton:
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __New__(self, *args, **kwds):
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
        with con:
            with con.cursor() as cur:
                cur.execute(sql)
                ret = cur.fetchall()
    except Exception as e:
        logging.error(f"Sql encounter error: {sql}")
    finally:
        return ret

def oracle(con: "psycopg2.connection", enc_var: str, data_type: str) -> str:
    """decrpty enc_var to plain text"""
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