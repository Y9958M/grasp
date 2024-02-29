# -*- coding:utf-8 -*-
import time
import traceback
import datetime
import json

from weakref import WeakKeyDictionary
from eventlet import tpool  # type: ignore
from nameko.dependency_providers import DependencyProvider  # type: ignore
from nameko.rpc import rpc, RpcProxy  # type: ignore

from graspBasic import HandleLog,msgWrapper,MESSAGE
from graspFun import supChkAndIns, proChkAndIns, invCheck,supSwap,proSwap,graspSupInvStatus
from graspAcc import graspAccountMain

log = HandleLog('grasp-service')

class LoggingDependency(DependencyProvider):

    def __init__(self):
        self.timestamps = WeakKeyDictionary()

    def worker_setup(self, worker_ctx):

        self.timestamps[worker_ctx] = datetime.datetime.now()

        service_name = worker_ctx.service_name
        method_name = worker_ctx.entrypoint.method_name

        log.info("%s.%s starting"%(service_name, method_name))

    def worker_result(self, worker_ctx, result=None, exc_info=None):

        service_name = worker_ctx.service_name
        method_name = worker_ctx.entrypoint.method_name

        if exc_info is None:
            status = "completed"
        else:
            status = "errored"
            log.error(traceback.print_tb(exc_info[2]))

        now = datetime.datetime.now()
        worker_started = self.timestamps.pop(worker_ctx)
        elapsed = (now - worker_started).seconds

        log.info("%s.%s %s after %ds"%(service_name, method_name, status, elapsed))

def some_fun_you_can_not_control():
    start = time.time()
    while True:
        if time.time() - start > 300:
            break

class GRASPService(object):
    log = LoggingDependency()
    name = "GRASP"              # 定义微服务名称 
    YM = RpcProxy("YM")

    @rpc
    @msgWrapper(ldt=240228,s_func_remark='测试连接用')
    def hello_world(self, msg):
        res_ym = self.YM.hello_world(msg)
        j_res = {'code':200,'msg':f'Hello World!I Am {self.name}: {msg} from Platform producer! 确认已连接','pf_msg':res_ym,'service':self.name}
        log.debug(j_res)
        return j_res
    
    @rpc
    def computation_bound(self):
        # 该任务一经发起会被不停重试，消耗计算资源
        start = time.time()
        while True:
            if time.time() - start > 300:
                break

    @rpc
    def computation_bound_sleep(self):
        # 使用 sleep 交出控制流让框架能够发送心跳
        start = time.time()
        while True:
            if int(time.time() - start) % 5 == 0:
                time.sleep(0.2)

            if time.time() - start > 300:
                break

    @rpc
    def computation_bound_tpool(self):
        # 使用 tpool 切换为线程运行
        return tpool.execute(some_fun_you_can_not_control)

    @rpc
    def raise_exception(self):
        raise Exception()


    # grasp ----------lj_args [{},{}]----------------------------------------------------------------------
    @rpc
    @msgWrapper(ldt=20240228,s_func_remark='供应商信息')
    def cInfoSup(self, lj_args=[]):    
        message = MESSAGE.copy()
        rc_continue = 0 # 非法的数量
        rc_in = 0       # 存在的数量
        rc_sucess = 0   # 插入的数量
        for j_ in lj_args:
            if 'tax_code' in j_:
                message.update(supChkAndIns(j_))
                log.debug(message)
                if message['code'] > 200:
                    return message
                else:
                    rc_in += message['in']
                    rc_sucess += message['no_in']
            else:
                rc_continue += 1
                continue
        message['remark'] = f"非法 记录数:{rc_continue} 存在 记录数：{rc_in} 插入 成功数：{rc_sucess}"
        message['count'] = rc_continue + rc_sucess + rc_in
        # 更新 REDIS
        # if rc_sucess > 0 or len(lj_args)==0:
        #     socialCreditCodeToRedis()
        # message['code'] = 200
        return message

    @rpc
    @msgWrapper(ldt=20240229,s_func_remark='商品信息')
    def cInfoPro(self, lj_args):
        message = MESSAGE.copy()
        rc_continue = 0 # 非法的数量
        rc_in = 0       # 存在的数量
        rc_sucess = 0   # 插入的数量
        
        for j_ in lj_args:
            if 'grasp_pro' in j_:
                message.update(proChkAndIns(j_))
                log.debug(message)
                if message['code'] > 200:
                    return message
                else:
                    rc_in += message['in']
                    rc_sucess += message['no_in']
            else:
                rc_continue += 1
                continue

        message['msg'] = f"非法 记录数:{rc_continue} 存在 记录数：{rc_in} 插入 成功数：{rc_sucess}"
        message['count'] = rc_continue + rc_sucess + rc_in
        return message

    @rpc
    @msgWrapper(ldt=20240229,s_func_remark='供应商单据生成')
    def cBlSupInvUp(self, j_args):
        message = MESSAGE.copy()
        # 检查已开票信息
        idno_list = []
        if 'tax_code_list' not in j_args:
            message['msg'] = '入参异常'
            return message
        for dic in j_args['tax_code_list']:
            idno_list.append(dic['inv_idno'])
        if idno_list is None or len(idno_list) < 1:
            message['msg'] = '未取得发票号'
            return message
        j_ = dict()
        j_ = invCheck(idno_list)
        if j_['code'] > 200:
            return j_
        # 开票明细目录组装  dtl = [{}] hdr = [{}]  cBillid
        bill_list = []
        userid =   j_args['INFO'][0]['userid']
        remark =    j_args['INFO'][0]['file_name']
        bltid =   j_args['INFO'][0]['bltid']
        hdr_list =[]
        inv_bill_dic = {}   # 发票和单号对应
        row_dic = {}
        # billid = ''
        # log.debug(billid,'billid')

        for dic in j_args['tax_code_list']:
            j_ym_res = json.loads(self.YM.cBillid('GRASP_BL_INVSUP_HDR',bltid))
            if j_ym_res['code']> 200:
                message.update({'msg':'通用单据取值失败'})
                log.error(j_ym_res)
                return message
            else:
                billid = j_ym_res.get('billid','-99')
            tax_code = dic.get('tax_code','')
            sup_no = supSwap(tax_code)
            if sup_no <1:
                message.update({'msg':f'tax_code:{tax_code} 未匹配供应商 sup_no'})
                return message
            inv_idno = dic.get('inv_idno','')
            row_dic = {}
            row_dic['billid'] = billid
            row_dic['bill_id'] = inv_idno
            row_dic['bltid'] = bltid
            row_dic['blsid'] = 1
            row_dic['supplier_no'] = sup_no
            row_dic['supplier_name'] = dic['sup_name']
            row_dic['buyer_no'] = 1
            row_dic['buyer_name'] = dic['pur_name']
            row_dic['out_storage_no'] = sup_no
            row_dic['in_storage_no'] = 1901    # < 默认总部仓库 
            row_dic['fromid'] = 3
            row_dic['inv_id'] = dic['inv_id']
            row_dic['inv_no'] = dic['inv_no']
            row_dic['inv_name'] = dic['inv_name']
            row_dic['inv_date'] = dic['inv_date']       # 2022年04月07日 
            row_dic['check_id'] = dic['check_id']
            row_dic['machine_no'] = dic['machine_no']
            row_dic['taxpayer_id'] = tax_code
            row_dic['fi_addr'] = dic['addr']
            row_dic['fi_tel']  = dic['tel']
            row_dic['accounts_back'] = dic['accounts_bank']
            row_dic['accounts_code'] = dic['accounts_code']
            row_dic['userid'] = userid
            row_dic['remark'] = remark
            inv_bill_dic[inv_idno] = billid
            bill_list.append(billid)
            hdr_list.append(row_dic)
        log.debug(inv_bill_dic,'inv_bill_dic')

        dtl_list = []
        for dic in j_args['pro_list']:
            row_dic ={}
            inv_idno = dic['inv_idno']
            grasp_pro = dic.get('grasp_pro','')
            pro_no = proSwap(grasp_pro)
            if pro_no <1:
                message.update({'msg':f'{grasp_pro} 未匹配商品 pro_no 请重新导入'})
                return message
            row_dic['billid'] = inv_bill_dic[inv_idno]
            row_dic['pro_no'] = pro_no
            row_dic['pro_name'] = dic['pro_name']
            row_dic['spec'] = dic['spec']
            row_dic['units'] = dic['units']
            row_dic['qty_pur'] = dic['qty_pur']
            row_dic['price_pur'] = dic['price_pur']
            row_dic['amt'] = dic['amt']
            row_dic['tax'] = dic['tax']
            row_dic['rat_tax_pur'] = dic['rat_tax_pur']
            row_dic['flow_no'] = dic['flow_no']
            dtl_list.append(row_dic)

        # 更新主表 状态为未审核 一个事务
        j_.clear()
        j_ = graspSupInvStatus(hdr_list,dtl_list)
        if j_['code'] > 200:
            return j_
        message['code'] = 200
        message['count'] = len(j_args['pro_list'])
        message['bill_list'] = bill_list
        return message


    # @rpc
    # def cBlBraInvUp(self, args_dict):
    #     return msgJson(blBraInvUp(args_dict))

    @rpc    # 通用入账
    @msgWrapper(ldt=20240229,s_func_remark='通用入账')
    def cGraspAccount(self, billid:int,actid:int):
        return graspAccountMain(billid,actid)

