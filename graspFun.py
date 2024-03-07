# -*- coding:utf-8 -*-
from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session


from graspBasic import MESSAGE, SID, HandleLog, engine

from graspMod import (GraspSupplier,GraspProduct,GraspBranch,GraspOnhand,GraspWba
                      ,GraspBlInvbraHdr,GraspBlInvbraDtl,GraspBlInvsupHdr,GraspBlInvsupDtl)

log = HandleLog(__name__,i_c_level=10,i_f_level=20)

# author  :don
# date    :2022-09-30
# description: 单元操作 数据库存相关操作 


# 检查发票信息 传入LIST 重复就返回号码
def invCheck(arg_list):
    message = MESSAGE.copy()
    message['fun'] = 'invCheck'
    log.debug(f">>> {message['fun']} 检查发票信息 传入LIST 重复就返回号码 入参： {arg_list}")

    stmt = select(GraspBlInvsupHdr.inv_idno).where(GraspBlInvsupHdr.inv_idno.in_(arg_list))
    with  Session(engine()) as se:
        qry = se.scalars(stmt).first()
        if qry:
            message['msg'] = f'检查发票 系统中已存在 {qry} '
        else:
            message['code'] = 200
    log.debug(f" <<< {message['fun']} ")
    return message


# # 更新 开票商品表 数据库保证唯一 ID自增长
# def graspProChkAndIns(j_args):
#     message = MESSAGE.copy()
#     message['fun'] = 'graspProChkAndIns'
#     log.debug(f">>> {message['fun']} 检查 grasp 开票商品 没有需要自动生成  {j_args}")
    
#     stmt = select(GraspProduct.pro_id).where(GraspProduct.barcode == j_args['barcode']) 
#     with  Session(engine) as se:
#         # qry = se.scalars(stmt).first()
#         qry = se.execute(stmt).fetchone()
#         if qry:
#             message['code'] = 200
#             message['in'] = 1
#             message['no_in'] = 0        
#             message['msg'] = f"已存在商品 {j_args['pro_name']}"
#             # 更新价格 220627 更新 按导入更新价格
#             su = update(GraspProduct).values(price_pur = j_args['price_pur']).where(GraspProduct.pro_id == qry[0])            
#             try:
#                 se.execute(su)
#                 se.commit()
#             except Exception as e:
#                 se.rollback()
#                 message['msg'] = '更新 开票商品进价 出错'
#                 message['remark'] = str(e)    
#         else:
#             # 从redis里取pro_no 有就更新 没有报错
#             pro_no = proSwap(j_args['barcode'])
#             if not pro_no :
#                 message['msg'] = '缓存REDIS中未取到 开票商品NO'
#                 return message
#             # 插入 开票商品
#             si = insert(GraspProduct).values(sid=SID, pro_no=pro_no, pro_id = pro_no, pro_sname= j_args['pro_name'],
#             price_pur = j_args['price_pur'],tax_pur_ratio = j_args['tax_pur_ratio'],tax_sale_ratio =j_args['tax_pur_ratio'],
#             remark = 'grasp 开票商品')
#             try:
#                 se.execute(si)
#                 se.commit()
#                 message['in'] = 0
#                 message['no_in'] = 1
#                 message['code'] = 200
#             except Exception as e:
#                 se.rollback()
#                 message['msg'] = '新增 开票商品 出错'
#                 message['remark'] = str(e)
#     return message


# 名称替换NO
def swapSup(sup_tax_code:str)->int:
    stmt = select(GraspSupplier.sup_no).where(GraspSupplier.social_credit_code == sup_tax_code) 
    with  Session(engine()) as se:
        sup_no = se.scalars(stmt).first()
    if not sup_no:
        sup_no = 0
    return sup_no

def swapPro(grasp_pro:str)->int:
    stmt = select(GraspProduct.pro_no).where(GraspProduct.grasp_pro == grasp_pro) 
    with  Session(engine()) as se:
        pro_no = se.scalars(stmt).first()
    if not pro_no:
        pro_no = 0
    return pro_no

def swapBra(bra_name:str)->int:
    stmt = select(GraspBranch.bra_no).where(GraspBranch.bra_name == bra_name) 
    with  Session(engine()) as se:
        bra_no = se.scalars(stmt).first()
    if not bra_no:
        bra_no = 0
    return bra_no


# 生成供应商发票商品单据
def graspInvSupStatus(hdr_ls,dtl_ls):
    message = MESSAGE.copy()
    message['fun'] = 'graspSupInvStatus'
    log.debug(f">>> {message['fun']} 生成供应商发票商品单据 {hdr_ls}")
    
    with engine().connect() as conn:
        res_hdr = conn.execute(  # noqa: F841
            insert(GraspBlInvsupHdr).values(sid=SID),hdr_ls
        )
        res_dtl = conn.execute(  # noqa: F841
            insert(GraspBlInvsupDtl).values(sid=SID),dtl_ls
        )
        try:
            conn.commit()
            message['code'] = 200
        except Exception as e:
            conn.rollback()
            message['msg'] = '更新单据失败'
            message['Exception'] = str(e)
            log.error(message)
    return message   


# 更新门店发票商品单据状态
def graspInvBraStatus(hdr_ls,dtl_ls):
    message = MESSAGE.copy()
    message['fun'] = 'graspBraInvStatus'
    log.debug(f">>> {message['fun']} 更新门店发票商品单据状态 ")
    
    with engine().connect() as conn:
        conn.execute(insert(GraspBlInvbraHdr).values(sid=SID),hdr_ls)
        conn.execute(insert(GraspBlInvbraDtl).values(sid=SID),dtl_ls)
        try:
            conn.commit()
            message['code'] = 200
        except Exception as e:
            conn.rollback()
            message['msg'] = '更新单据失败'
            message['Exception'] = str(e)
    return message   


# def cortSwap(cort_tax=None):
#     rs.hmset('BILL_KEY',DEF['BILL_KEY'])
#     m =  rs.hmget('BILL_KEY','GRASP_INVSUP')
#     log.debug(m)
#     return 1



# 取门店信息 从REDIS取  返回一个DICT 和 一个子DICT
def braNoInfo(bra_no)-> dict:
    stmt = select(GraspBranch).where(GraspBranch.bra_no == bra_no)
    with  Session(engine()) as se:
        j_ = {'bra_no':bra_no}
        qry = se.scalars(stmt).first()
        j_['bra_name'] = qry.bra_name
        j_['tax_code'] = qry.tax_code
        j_['fi_addr'] = qry.fi_addr
        j_['fi_tel'] = qry.fi_tel
        j_['accounts_bank'] = qry.accounts_bank
        j_['accounts_code'] = qry.accounts_code
        return j_


def proNoInfo(grasp_pro):
    stmt = select(GraspProduct).where(GraspProduct.grasp_pro == grasp_pro) 
    with engine().connect() as cur:
        ds = cur.execute(stmt).fetchone()
        if ds:
            return ds._asdict()
        else:
            return {}



# 检查供应商信息 没有就返回对应供应商list
def supChkAndIns(j_args)-> dict:
    message = MESSAGE.copy()
    message['fun'] = 'supChkAndIns'
    log.debug(f">>> {message['fun']} 检查供应商信息 没有就返回对应供应商list {j_args}")
    
    stmt = select(GraspSupplier.tax_code).where(GraspSupplier.tax_code == j_args['tax_code']) 
    with  Session(engine()) as se:
        qry = se.scalars(stmt).first()
    if qry:
        message['code'] = 200
        message['in'] = 1
        message['no_in'] = 0        
        message['msg'] = f"已存在 {j_args['tax_code']}"
    else:
        # 插入供应商
        si = insert(GraspSupplier).values(sid=SID, cort_no=j_args['cort_no'],
        sup_name= j_args['sup_name'],sup_sname= j_args['sup_name'],
        social_credit_code= j_args['tax_code'], tax_code= j_args['tax_code'],
        fi_addr = j_args.get('fi_addr',''),fi_tel = j_args.get('fi_tel',''),
        accounts_bank = j_args.get('accounts_bank',''), accounts_code = j_args.get('accounts_code',''))
        try:
            se.execute(si)
            se.commit()
            message['in'] = 0
            message['no_in'] = 1
            message['code'] = 200
        except Exception as e:
            se.rollback()
            message['msg'] = '新增供应商出错'
            message['remark'] = str(e)
    return message

# 检查 商品 信息 没有就插入
def proChkAndIns(j_args)-> dict:
    message = MESSAGE.copy()
    message['fun'] = 'proChkAndIns'
    log.debug(f">>> {message['fun']} 检查 商品 信息 没有就插入 {j_args}")
    
    stmt = select(GraspProduct.grasp_pro).where(GraspProduct.grasp_pro == j_args.get('grasp_pro','')) 
    with  Session(engine()) as se:
        qry = se.scalars(stmt).first()
    if qry:
        message['code'] = 200
        message['in'] = 1
        message['no_in'] = 0
    else:# 插入商品
        si = insert(GraspProduct).values(sid=SID, pro_name=j_args['pro_name'],spec= j_args.get('spec',''), units= j_args.get('units','')
        ,price_pur=j_args['price_pur'],rat_tax_pur=j_args.get('rat_tax_pur',-99),rat_tax_sale=j_args.get('rat_tax_pur',-99))
        try:
            se.execute(si)
            se.commit()
            message['code'] = 200
            message['in'] = 0
            message['no_in'] = 1
        except Exception as e:
            se.rollback()
            message['msg'] = '新增 商品 出错'
            message['remark'] = str(e)
            log.error(message)
    return message

# 编辑 商品 信息
def proEdit(j_args)-> dict:
    message = MESSAGE.copy()
    message['fun'] = 'proEdit'
    log.debug(f">>> {message['fun']} 编辑 商品 信息 {j_args}")

    se = Session(engine())
    stmt = select(GraspProduct).where(GraspProduct.pro_no == j_args.get('pro_no',0)).where(GraspProduct.sid == j_args.get('sid',0))
    se_pro = se.scalars(stmt).first()
    if se_pro:
        try: # 没传的值就不更新了
            if s:=j_args.get('price_pur_excl',''):
                se_pro.price_pur_excl = s
            if s:=j_args.get('rat_tax_pur',''):
                se_pro.rat_tax_pur = s
            if s:=j_args.get('rat_tax_sale',''):
                se_pro.rat_tax_sale = s
            if s:=j_args.get('userid',''):
                se_pro.remark = f"{s} 从{j_args.get('code_from','')} 更新"
            se.commit()
            message.update({'code':200,'msg':f"更新 {j_args['pro_no']} 成功"})
        except Exception as e:
            message.update({'msg':str(e)})
            log.warning(message,'更新异常')
    else:
        message.update({'msg':f"未查到记录 {j_args['pro_no']}"})
        log.warning(message,'无值')
    return message


# 编辑 商品 信息
def blInvBraEdit(j_args)-> dict:
    message = MESSAGE.copy()
    message['fun'] = 'blInvBraEdit'
    log.debug(f">>> {message['fun']} 编辑 门店开票商品 信息 {j_args}")

    se = Session(engine())
    stmt = select(GraspBlInvbraDtl).where(GraspBlInvbraDtl.id == j_args.get('id',0))
    se_pro = se.scalars(stmt).first()
    if se_pro:
        try: # 没传的值就不更新了
            if s:=j_args.get('qty_sale',0):
                se_pro.qty_sale = s
            if s:=j_args.get('price_sale_excl',0):
                se_pro.price_sale_excl = s
            if s:=j_args.get('userid',''):
                se_pro.remark = f"{s} 从{j_args.get('code_from','')} 更新"
            se.commit()
            message.update({'code':200,'msg':"更新 成功"})
        except Exception as e:
            message.update({'msg':str(e)})
            log.warning(message,'更新 异常')
    else:
        message.update({'msg':"未查到记录"})
        log.warning(message,'无值')
    return message