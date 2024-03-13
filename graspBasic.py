# -*- coding:utf-8 -*-
import logging,colorlog     # noqa: E401
import os,time,json,decimal              # noqa: E401
import redis
import sqlalchemy
from datetime import datetime,date
# from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from logging.handlers import RotatingFileHandler

# author  :don
# date    :2024-02-14
# desc  : 管家婆

DEF = {"BILL_KEY": {"OPL_BL_REP_HDR": 110, "GRASP_BL_INVBRA_HDR": 141, "GRASP_BL_INVSUP_HDR": 140}}
PROJECT = "GRASP"
# SID 环境标识 1生产 2测试 3删除 4作废 5本机开发 API 1 CMM 3 
SID = 2

# 5本机
if SID == 5:
    VER = 240214
    CLIENT ="Dev:10.56"
    DB_LINK = {
        'GRASP':{
            "USE" : {},
            "TYPE": "MYSQL",
            "HOST": "127.0.0.1",
            "PORT": 3310,
            "USER": "root",
            "PWD": "4197",
        },
        'REDIS': {
            "DB": SID,
            "HOST": "127.0.0.1",
            "PWD": "",
            "PORT": 6378,
            "TYPE": "REDIS"
        },
    }
# 2测试 expire
elif SID == 2:
    VER = 240214
    CLIENT ="Beta:10.56"
    DB_LINK = {
        'GRASP':{
            "USE" : {},
            "TYPE": "MYSQL",
            "HOST": "192.168.10.49",
            "PORT": 3306,
            "USER": "root",
            "PWD": "shtm2022",
        },
        'REDIS': {
            "DB": SID,
            "HOST": "172.17.0.1",
            "PWD": "shtm2022",
            "PORT": 6378,
            "TYPE": "REDIS"
        },
    }
#   1生产
elif SID == 1:
    pass
else:
    pass

MESSAGE = {
    "code": 500,
    "msg":  '',
    "info":{
        "sid":  SID,
        "project":PROJECT,
        "client":CLIENT,
        "ver":VER,
        "author":'姚鸣'},
    }

# -*- 把Date、DateTime类型数据转换成兼容Json的格式 -*-  json.dumps(result,cls=DateEncoder.DateEncoder) # 调用自定义类
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, int):
            return int(obj)
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj,sqlalchemy.engine.row.Row):
            return list(obj)
        elif isinstance(obj,sqlalchemy.engine.row.RowMapping):
            return dict(obj)
        elif isinstance(obj,sqlalchemy.engine.result.RMKeyView):
            return list(obj)
        else:
            return json.JSONEncoder.default(self, obj)

def msgJson(data):
    return json.dumps(data,cls=DateEncoder,ensure_ascii=False)


def msgWrapper(ldt:int,s_func_remark=''):
    def reMsg(func):
        def wrapped_function(*args, **kwargs):
            j_msg = MESSAGE.copy()
            j_msg['info']['fac'] = func.__name__
            start_time = time.time()
            start_strftime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            j_res = func(*args, **kwargs)

            end_strftime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            d_time = time.time() - start_time
            j_msg.update(j_res)
            j_msg['info'].update({'start_time':start_strftime,'end_time':end_strftime,'times':round(d_time,2),"ldt":ldt,'func_remark':s_func_remark})
            return msgJson(j_msg)
        return wrapped_function
    return reMsg


def l2d(j_ds):
    if 'data' not in j_ds:
        return j_ds
    if 'fields' not in j_ds['data'] or 'datalist' not in j_ds['data']:
        return j_ds
    fields = j_ds['data']['fields']
    datalist = j_ds['data']['datalist']
    l_ds = [dict(zip(fields, sublist)) for sublist in datalist]
    j_ds['data']['datalist'] = l_ds
    return j_ds


def engine(DB=PROJECT.lower(),LINK=""):
    LINK = LINK if LINK else PROJECT
    JDBC ={'MYSQL':'mysql+pymysql','MSSQL':'mssql+pymssql'}
    PARM ={'MYSQL':'','MSSQL':'?charset=cp936'}
    s_ = f"{JDBC[DB_LINK[LINK]['TYPE']]}://{DB_LINK[LINK]['USER']}:{DB_LINK[LINK]['PWD']}@{DB_LINK[LINK]['HOST']}:{DB_LINK[LINK]['PORT']}/{DB}{PARM[DB_LINK[LINK]['TYPE']]}"
    return sqlalchemy.create_engine(s_, poolclass=QueuePool, max_overflow=10, pool_size=24, pool_timeout=30, pool_recycle=3600)


logging._srcfile = None
logging.logThreads = False
logging.logMultiprocessing = False
logging.logProcesses = False
logging.thread = None  # type: ignore
log_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logs')  # log_path为存放日志的路径
if not os.path.exists(log_path): os.mkdir(log_path)  # 若不存在logs文件夹，则自动创建  # noqa: E701
s_log_file = os.path.join(log_path,f"plm-{datetime.now().strftime('%Y%m%d')}.log")


rs = redis.Redis(connection_pool=redis.ConnectionPool(
    host    =   DB_LINK['REDIS']['HOST'],
    password =  DB_LINK['REDIS']['PWD'],
    port =      DB_LINK['REDIS']['PORT'],
    db =        DB_LINK['REDIS']['DB'],
    decode_responses=True,
    encoding='utf-8'))


# 初始化配置 数据从后台取 初始化的时候 取项目库JSON数据# 连接后台 启动级异常 不需要返回 直接记日志
class HandleLog:
    def __init__(self,s_name, s_path=s_log_file, i_c_level = 60 - SID*10, i_f_level = 60 - SID*10):
        self.logger = logging.getLogger(s_name) # 创建日志记录器
        self.logger.setLevel(logging.DEBUG)
        # self.__logger = logging.getLogger() 
        formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s %(name)6s: %(message_log_color)s%(message)s',
        datefmt='%y%m%d %H:%M:%S',
        reset=True,
        log_colors={
            'DEBUG':    'black',
            'INFO':     'cyan',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={'message':{
            'DEBUG':    'light_black',
            'INFO':     'light_cyan',
            'WARNING':  'light_yellow',
            'ERROR':    'light_red',
            'CRITICAL': 'light_purple'
        }},
        style='%')

        #设置CMD日志
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(i_c_level)

        #设置文件日志
        fh = RotatingFileHandler(filename=s_path, mode="w", maxBytes=5*1024*1024, backupCount=5,encoding='utf-8')
        formatter_file = logging.Formatter('%(asctime)s %(name)s %(levelname)9s: %(message)s', datefmt='%a %y%m%d %H:%M:%S')
        fh.setFormatter(formatter_file)
        fh.setLevel(i_f_level)

        self.logger.propagate = False
        if not self.logger.handlers: # 防止日志重复打印 logger.propagate 布尔标志, 用于指示消息是否传播给父记录器
            self.logger.addHandler(sh)
            self.logger.addHandler(fh)
    
    def debug(self,message,title=''):
        self.logger.debug(f"{title}:{message}" if title else message)

    def info(self,message,title=''):
        self.logger.info(f"{title}:{message}" if title else message)

    def warning(self,message,title=''):
        self.logger.warning(f"{title}:{message}" if title else message)

    def error(self,message,title=''):
        self.logger.error(f"{title}:{message}" if title else message)

    def cri(self,message,title=''):
        self.logger.critical(f"{title}:{message}" if title else message)

