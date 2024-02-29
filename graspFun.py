# -*- coding:utf-8 -*-
from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session


from graspBasic import MESSAGE, SID, HandleLog, engine

from graspMod import (GraspSupplier,GraspProduct,GraspBranch,GraspOnhand,GraspWba
                      ,GraspBlInvbraHdr,GraspBlInvbraDtl,GraspBlInvsupHdr,GraspBlInvsupDtl)
# from common.fac import commonQueryKV

log = HandleLog(__name__,i_c_level=10,i_f_level=20)


# redis_pool = redis.ConnectionPool(
#     host    =   DB_LINK['REDIS']['HOST'],
#     password =  DB_LINK['REDIS']['PWD'],
#     port =      DB_LINK['REDIS']['PORT'],
#     db =        DB_LINK['REDIS']['DB'],
#     decode_responses=True,
#     encoding='utf-8')
# rs = redis.Redis(connection_pool=redis_pool)
# pipe = rs.pipeline()

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


# # 检查grasp供应商 没有需要自动生成 
# def graspSupChkAndIns(j_args):
#     message = MESSAGE.copy()
#     message['fun'] = 'graspSupChkAndIns'
#     log.debug(f">>> {message['fun']} 检查 grasp供应商 没有需要自动生成  {j_args}")
    
#     stmt = select(GraspSupplier.tax_code).where(GraspSupplier.tax_code == j_args['tax_code']) 
#     with  Session(engine) as se:
#         qry = se.scalars(stmt).first()
#         if qry:
#             message['code'] = 200
#             message['in'] = 1
#             message['no_in'] = 0        
#             message['msg'] = f"已存在供应商 {j_args['tax_code']}"
#         else:
#             # 从redis里取sup_no 有就更新 没有报错
#             sup_no = supSwap(j_args['tax_code'])
#             if not sup_no :
#                 message['msg'] = '缓存REDIS中未取到 供应商NO'
#                 return message
#             # 插入供应商
#             si = insert(GraspSupplier).values(sid=SID, sup_no=sup_no, sup_id = sup_no, sup_sname= j_args['sup_name'],addr=j_args['addr'],tel=j_args['tel'],
#             remark = 'grasp 插入供应商')
#             try:
#                 se.execute(si)
#                 se.commit()
#                 message['in'] = 0
#                 message['no_in'] = 1
#                 message['code'] = 200
#             except Exception as e:
#                 se.rollback()
#                 message['msg'] = '新增供应商出错'
#                 message['remark'] = str(e)
#     return message


# # def proToRedis(grasp_pro = None,time_expire = None):
# #     message = MESSAGE.copy()
# #     message['fun'] = 'proToRedis'
# #     log.debug(f">>> {message['fun']} 更新 REDIS ")
# #     if not grasp_pro: 
# #         pipe.delete('grasp_pro')
# #     with  Session(engine()) as se:
# #         stmt = select(GraspProduct).where(GraspProduct.pro == grasp_pro) if grasp_pro else select(GraspProduct)
# #         res = se.execute(stmt).scalars().fetchall()
# #         if not res:
# #             return False
# #     for row in res:
# #         pipe.hset('grasp_pro',str(row.pro),str(row.pro_no))
# #     pipe.execute()
# #     if time_expire is not None:
# #         pipe.expire('grasp_pro', time_expire)
# #     return True




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
def supSwap(sup_tax_code:str)->int:
    stmt = select(GraspSupplier.sup_no).where(GraspSupplier.social_credit_code == sup_tax_code) 
    with  Session(engine()) as se:
        sup_no = se.scalars(stmt).first()
    if not sup_no:
        sup_no = 0
    return sup_no

def proSwap(grasp_pro:str)->int:
    stmt = select(GraspProduct.pro_no).where(GraspProduct.grasp_pro == grasp_pro) 
    with  Session(engine()) as se:
        pro_no = se.scalars(stmt).first()
    if not pro_no:
        pro_no = 0
    return pro_no


    # try:
    #     if rs.exists('grasp_pro'):
    #         _b = rs.hget('grasp_pro',grasp_pro)
    #         if _b:
    #             return _b
    #         else:
    #             with Session(engine()) as se:
    #                 stmt = select(GraspProduct.pro_no).where(GraspProduct.pro == grasp_pro)
    #                 # stmt = select(t_v_pro.c.pro_no).where(t_v_pro.c.barcode == barcode)
    #                 pro_no = se.scalars(stmt).first()
    #                 log.info(pro_no)
    #                 if pro_no:
    #                     rs.hset('barcode',grasp_pro,pro_no)
    #                     return pro_no
    #                 else:
    #                     log.warning(f"grasp_product not {grasp_pro}")
    #                     return None
    #     else:
    #         log.error(f"barcode {grasp_pro} fail")
    #         return None
    # except Exception as e:
    #     log.error(f"proSwap {str(e)}")
    #     return None



# 生成供应商发票商品单据
def graspSupInvStatus(hdr_ls,dtl_ls):
    message = MESSAGE.copy()
    message['fun'] = 'graspSupInvStatus'
    log.debug(f">>> {message['fun']} 生成供应商发票商品单据 {hdr_ls}")
    
    with engine().connect() as conn:
        res_hdr = conn.execute(
            insert(GraspBlInvsupHdr).values(sid=SID),hdr_ls
        )
        res_dtl = conn.execute(
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


# # 更新门店发票商品单据状态
# def graspBraInvStatus(hdr_ls,dtl_ls):
#     message = MESSAGE.copy()
#     message['fun'] = 'graspBraInvStatus'
#     log.debug(f">>> {message['fun']} 更新门店发票商品单据状态 ")
    
#     with engine.connect() as conn:
#         res_hdr = conn.execute(
#             insert(GraspBlInvbraHdr).values(sid=SID),hdr_ls
#         )
#         res_dtl = conn.execute(
#             insert(GraspBlInvbraDtl).values(sid=SID),dtl_ls
#         )
#         try:
#             conn.commit()
#             message['code'] = 200
#         except Exception as e:
#             conn.rollback()
#             message['msg'] = '更新单据失败'
#             message['Exception'] = str(e)
#     return message   


# def cortSwap(cort_tax=None):
#     rs.hmset('BILL_KEY',DEF['BILL_KEY'])
#     m =  rs.hmget('BILL_KEY','GRASP_INVSUP')
#     log.debug(m)
#     return 1



# # 取门店信息 从REDIS取  返回一个DICT 和 一个子DICT
# def braNoInfo(bra_no):
#     bra_dict ={}
#     bra_key = f'bra_no:{bra_no}'
#     try:
#         if rs.exists(bra_key):
#             bra_dict['sid'] = rs.hmget(bra_key,'sid')
#             bra_dict['bra_no']  = rs.hmget(bra_key,'bra_no')
#             bra_dict['bra_name'] = rs.hmget(bra_key,'bra_name')
#             bra_dict['tax_code'] = rs.hmget(bra_key,'tax_code')
#             bra_dict['addr']    = rs.hmget(bra_key,'fi_addr')
#             bra_dict['tel']     = rs.hmget(bra_key,'fi_tel')
#             bra_dict['accounts_bank'] = rs.hmget(bra_key,'accounts_bank')
#             bra_dict['accounts_code'] = rs.hmget(bra_key,'accounts_code')
#     except Exception as e:
#         log.error(str(e))
#     return bra_dict


# def proNoInfo(pro_no):
#     log.debug(f"proNoInfo {pro_no}")
#     qry_list = []
#     res = {}
#     stmt = select(GraspProduct).where(GraspProduct.pro_no == pro_no) 
#     with engine.connect() as cur:
#         ds = cur.execute(stmt).fetchone()
#         if ds:
#             return ds._asdict()
#             # for row in ds:
#             #     res = row._asdict()
#             #     log.debug(res)
#             #     return res
#         else:
#             return {}



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
        addr = j_args.get('addr',''),tel = j_args.get('tel',''),
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


# def socialCreditCodeToRedis(time_expire =None):
#     message = MESSAGE.copy()
#     message['fun'] = 'socialCreditCodeToRedis'
#     log.debug(f">>> {message['fun']} 更新 REDIS ")

#     with  Session(engine()) as se:
#         res = se.execute(select(GraspSupplier)).scalars().fetchall()
#     for row in res:
#         pipe.hmset('social_credit_code', {str(row.social_credit_code):str(row.sup_no)})
#         # log.debug(maps)
#     pipe.execute()
#     if time_expire is not None:
#         pipe.expire('social_credit_code', time_expire)
#     return True
    # log.debug(res)
    #   r.expire("list5", time=3)
    #   删除 hdel(name,*keys)
    #   存在 hexists(name, key)
    #   hvals(name)     得到所有的value（类似字典的取所有value）
    #   hkeys(name)     得到所有的keys（类似字典的取所有keys）
    #   hlen(name)      得到所有键值对的格式 hash长度
    #   hgetall(name)   取出所有的键值对
    #   hmget(name, keys, *args)
    #     print(r.hget("hash2", "k2"))  # 单个取出"hash2"的key-k2对应的value
    # print(r.hmget("hash2", "k2", "k3"))  # 批量取出"hash2"的key-k2 k3对应的value --方式1
    # print(r.hmget("hash2", ["k2", "k3"]))  # 批量取出"hash2"的key-k2 k3对应的value --方式2
    # redis.select(8);//使用第8个库
    # redis.flushDB();//清空第8个库所有数据 .where(GraspProduct.pro_id == qry['pro_id'])



# def braToRedis(time_expire =None):
#     message = MESSAGE.copy()
#     message['fun'] = 'braToRedis'
#     log.debug(f">>> {message['fun']} BRA更新 REDIS ")
#     bra_info = ""
#     with  Session(engine) as se:
#         res = se.execute(select(GraspBranch)).scalars().fetchall()
#     for row in res:
#         bra_info =f"bra_no:{row.bra_no}"
#         pipe.hmset(bra_info, {'sid':str(row.sid)})
#         pipe.hmset(bra_info, {'cort_no':str(row.cort_no)})
#         pipe.hmset(bra_info, {'bra_no':str(row.bra_no)})
#         if row.bra_id: pipe.hmset(bra_info, {'bra_id':str(row.bra_id)})
#         pipe.hmset(bra_info, {'bra_name':str(row.bra_name)})
#         pipe.hmset(bra_info, {'bra_sname':str(row.bra_sname)})
#         if row.type_no: pipe.hmset(bra_info, {'type_no':str(row.type_no)})
#         if row.status_no:pipe.hmset(bra_info, {'status_no':str(row.status_no)})
#         if row.tax_code: pipe.hmset(bra_info, {'tax_code':str(row.tax_code)})
#         if row.accounts_bank: pipe.hmset(bra_info, {'accounts_bank':str(row.accounts_bank)})
#         if row.accounts_code: pipe.hmset(bra_info, {'accounts_code':str(row.accounts_code)})
#         if row.fi_addr: pipe.hmset(bra_info, {'fi_addr':str(row.fi_addr)})
#         if row.fi_tel: pipe.hmset(bra_info, {'fi_tel':str(row.fi_tel)})
#         if row.open_date: pipe.hmset(bra_info, {'open_date':str(row.open_date)})
#         if row.total_area: pipe.hmset(bra_info, {'total_area':str(row.total_area)})
#         # log.debug(row.pro_no)
#     pipe.execute()
#     if time_expire is not None:
#         pipe.expire(bra_info, time_expire)
    
#     # log.debug(res)
#     return True


# 从后台拉数据缓存到CMM中
# def sqlidToRedis(rs_key :str,sqlid :str,time_expire =None):
#     message = {'code':400,'msg':'缓存处理异常'}
#     message['fun'] = 'sqlidToRedis'
#     log.debug(f">>> {message['fun']} 更新 REDIS SQLID= {sqlid}")
#     # ( ˇˍˇ )调用通用查询 
#     res = json.loads(msgJson(commonQueryKV({'sqlid':sqlid})))
#     if res['code'] > 200:
#         return res
#     for row in res['data']['datalist']:
#         bra_info =f"{rs_key}:{row[rs_key]}"
#         for k,v in row.items():
#             if v:
#                 pipe.hmset(bra_info, {k:v})
#         if time_expire is not None:
#             pipe.expire(bra_info, time_expire)
#     pipe.execute()
#     message['code'] = 200
#     return message


# def billNo(bill_key:int,typeid=1,proj_name="REDIS",time_expire=60*60*24):
#     bbkkyymmdd = f"{bill_key}{typeid}{time.strftime('%y%m%d', time.localtime())}"
#     redis_pool = redis.ConnectionPool(
#         host    =   DB_LINK[proj_name]['HOST'],
#         password =  DB_LINK[proj_name]['PWD'],
#         port =      DB_LINK[proj_name]['PORT'],
#         db =        DB_LINK[proj_name]['DB'],
#         decode_responses=True,
#         encoding='utf-8')
#     rs = redis.Redis(connection_pool=redis_pool)
#     try:
#         if rs.exists(bbkkyymmdd):
#             bk_series = rs.incr(bbkkyymmdd,amount=1)
#         else:
#             bk_series = 1
#             rs.set(bbkkyymmdd,1)
#             rs.expire(bbkkyymmdd, time_expire)
#     except Exception as e:
#         log.error(str(e))
#         return 0

#     res = f'{bbkkyymmdd}{str(bk_series).zfill(4)}{datetime.now().weekday() +1}'
#     return int(res)
