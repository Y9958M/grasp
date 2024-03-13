# -*- coding:utf-8 -*-
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from graspBasic import MESSAGE, SID, DEF, HandleLog, engine
# from public import DEF

from graspMod import GraspWba

log = HandleLog(__name__)


# author  :don
# date    :2022-06-01
# description: 通用入账 先入WBA流水 再增减库存 类型7反向
# 负库存检查

# BILL_KEY = {
#     'OPL': 100, 
#     'GRASP_BL_INVSUP_HDR': 140, 
#     'GRASP_BL_INVBRA_HDR': 141
#     }


def graspAccountMain(billid,act_no=0):
    message = MESSAGE.copy()
    message['fun'] = 'graspAccount'
    log.debug(f" {message['fun']} GRASP 通用入账 先入WBA流水 ONHAND 库存 单号 {billid} 动作 {act_no}")

    ACC = 1     # 帐务方向 正向1 反向 -1
    do_status_list = [1,]

    # 单据类型要在BILL_KEY中
    if not isinstance(act_no, int):
        message['msg'] = f"操作入参要是数字 比如审核是5 但接收的为 {act_no}"
    table_hdr = '销售的表头'
    table_dtl = '销售明细'
    bkk = '销售是 sale 采购是 pur'
    bk = int(str(billid)[0:3])     # bill_key 3位
    type_no = int(str(billid)[3:4])
    bb = False
    qty_b = False       # 检查库存数量

    for k,v in DEF['BILL_KEY'].items():
        if v == bk:
            table_hdr = k.lower()
            table_dtl = f"{table_hdr[:-3]}dtl"
            bb = True
            break
        else:
            continue
    if not bb:
        message['msg']=f"单据类型 {bk} 未注册"
        return message

    # 检查流水表 手工备份
    stmt = select(GraspWba).where(GraspWba.sid == SID, GraspWba.billid == billid, GraspWba.act_no == act_no )
    with  Session(engine()) as se:
        qry = se.scalars(stmt).first()
    if qry:
        message['msg'] = f"入帐流水中已存在 {billid} "
        return message

    # 按业务类型查出流水表要求数据  
    if bk == 140: # 140 供应商开票
        bkk = 'pur'
        if type_no == 1:        # 类型 退货
            if act_no == 6:     # 动作 审核
                ACC = 1         # 正向 +
                do_status_list = [1,2,3,4,5]
            elif act_no == 9:   # 动作 红冲
                ACC = -1        # 反向 -
                do_status_list = [6]
            else:
                message['msg'] = f"未配置 {table_hdr} 入账类型 {type_no} 的入账动作 {act_no}"
                return message
        elif type_no == 7:      # 类型 退货
            if act_no == 6:     # 动作 审核
                ACC = 1         # 入账 反向
                do_status_list = [1,2,3,4,5]
            elif act_no == 9:   # 动作 红冲
                ACC = -1        # 反向 -
                do_status_list = [6]
            else:
                message['msg'] = f"未配置 {table_hdr} 入账类型 {type_no} 的入账动作 {act_no}"
                return message
        else:
            ACC = 0
            message['msg'] = f"未配置 {table_hdr} 入账类型 {type_no}"
            return message

    elif bk == 141: # 141 门店销售
        bkk = 'sale'
        if type_no == 1:        # 类型 退货
            qty_b = True
            if act_no == 6:     # 动作 审核
                ACC = -1        # 正向 -
                do_status_list = [1,2,3,4,5]
            elif act_no == 9:   # 动作 红冲
                ACC = 1         # 反向 +
                do_status_list = [6]
                qty_b = False   # 20240307 门店红冲不检查库存
            else:
                message['msg'] = f"未配置 {table_hdr} 入账类型 {type_no} 的入账动作 {act_no}"
                return message
        elif type_no == 7:      # 类型 退货
            if act_no == 6:     # 动作 审核
                ACC = 1         # 入账 反向
                do_status_list = [1,2,3,4,5]
            else:
                message['msg'] = f"未配置 {table_hdr} 入账类型 {type_no} 的入账动作 {act_no}"
                return message
        else:
            ACC = 0
            message['msg'] = f"未配置 {table_hdr} 入账类型 {type_no}"
            return message

    else:
        message['msg'] = f"未配置入账模型 {billid}"
        return message

    qty_txt = f"""
        SELECT aa1.pro_no,aa1.pro_name,b1.qty_aval - aa1.qty as qty
        FROM (
            SELECT a1.sid,b1.pro_name,a1.{'in_storage_no' if bkk == 'pur' else 'out_storage_no' },b1.pro_no,
            SUM(b1.qty_{bkk}) qty
            FROM {table_hdr} a1 INNER JOIN {table_dtl} b1 ON a1.sid = b1.sid AND a1.billid = b1.billid
            WHERE a1.sid = {SID} AND a1.billid = {billid}
            GROUP BY a1.sid,b1.pro_name,a1.{'in_storage_no' if bkk == 'pur' else 'out_storage_no' },b1.pro_no
        ) aa1 LEFT JOIN grasp_onhand b1 
        ON aa1.sid = b1.sid AND aa1.{'in_storage_no' if bkk == 'pur' else 'out_storage_no' } = b1.storage_no AND aa1.pro_no = b1.pro_no
        WHERE b1.qty_aval - aa1.qty < 0 
        LIMIT 3
    """

    sql_txt = f"""
        INSERT INTO grasp_wba(sid,billid,acc_no,act_no,supplier_no,buyer_no,out_storage_no,in_storage_no,pro_no,pro_name,spec,units,qty,price,amt,tax,rat_tax)
    SELECT 
        a1.sid,a1.billid,{ACC} as acc_no,{act_no} as act_no,
        a1.supplier_no,a1.buyer_no,a1.out_storage_no,a1.in_storage_no,
        b1.pro_no
                ,max(b1.pro_name) pro_name
				,max(b1.spec) spec
				,max(b1.units) units
				,sum(b1.qty_{bkk}) qty
				,max(b1.price_{bkk}_excl) price
				,sum(b1.amt_excl) amt
				,sum(b1.tax) tax
				,max(b1.rat_tax_{bkk}) rat_tax
        FROM {table_hdr} a1 INNER JOIN {table_dtl} b1 ON a1.sid=b1.sid AND a1.billid = b1.billid
        WHERE a1.sid = {SID} AND a1.billid =  {billid}
				GROUP BY 
		a1.sid,a1.billid,a1.supplier_no,a1.buyer_no,a1.out_storage_no,a1.in_storage_no,b1.pro_no
        """
    sql_wba_3 =f"""
        UPDATE grasp_wba SET sid = 3  WHERE sid = {SID} AND billid = {billid};
    """
    sql_onhand_txt = f"""
        INSERT INTO grasp_onhand(sid,storage_no,pro_no,pro_name,spec,units,qty_aval,price_pur_last) 
        SELECT sid,{'in_storage_no' if bkk == 'pur' else 'out_storage_no' } as storage_no,pro_no,pro_name,spec,units,{ACC} * qty as qty_aval,price as price_pur_last 
        FROM grasp_wba
        WHERE sid = {SID} AND billid = {billid} AND act_no = {act_no}
        ON DUPLICATE KEY UPDATE qty_aval= qty_aval + {ACC} * qty {',price_pur_last =price' if ACC == 1 else ''}
    """
    check_txt =  f"SELECT blsid FROM {table_hdr} WHERE sid = {SID} AND billid =  {billid};"
    begin_txt =  f"UPDATE {table_hdr} SET blsid = -{act_no} WHERE sid = {SID} AND billid = {billid};"
    end_txt =    f"UPDATE {table_hdr} SET blsid =  {act_no} WHERE sid = {SID} AND billid = {billid};"

    # log.debug(qty_txt)
    log.debug(f"bk:{bk} type_no:{type_no} table_name{table_hdr} act_no{act_no} sql_txt: \n {sql_txt}")
    # 插入流水表 
    with engine().connect() as conn:
        # 检查单据状态 
        qry_status = conn.execute(text(check_txt)).fetchone()
        if qry_status:
            if qry_status[0] not in do_status_list or not qry_status[0]:
                message['msg'] = f"单据状态 {qry_status[0]} 不在列表 {do_status_list} 中 不可入账"  # type: ignore
                return message
            elif qty_b: # 检查可用库存
                qry_qty = conn.execute(text(qty_txt)).fetchall()
                if len(qry_qty) > 0:
                    err_msg = ''    # 拼接下商品信息转STR
                    for dic in qry_qty:
                        # log.debug(dic)
                        # err_msg += f"商品: {dic['pro_no']} 缺少数量: {str(dic['qty'])} ,"
                        err_msg += f"{dic[1]} 缺:{str(dic[2])} ,"
                    message['msg'] = err_msg
                    return message
            else:
                conn.execute(text(begin_txt))
                conn.commit()    
        else:
            message['msg'] = f"查询语句 {check_txt} 未取到数据！"
            return message
        # 更新WBA
        try:
            conn.execute(text(sql_txt))
            conn.commit()
        except Exception as e:
            conn.rollback()
            message['msg']=f"WBA 表更新异常\n{str(e)}"
            log.error(message,"WBA 表更新异常")
            return message

        # 关联更新 ONHAND 表 异常处理？
        try:
            conn.execute(text(sql_onhand_txt))
            conn.commit()
        except Exception as e:
            conn.rollback()
            #失败的WBA打标记
            conn.execute(text(sql_wba_3))
            conn.commit()
            message['msg']=f"ONHAND 库存S更新异常\n{str(e)}"
            log.error(message,'库存更新异常')
            return message

        # 更新到结果状态    
        conn.execute(text(end_txt))
        conn.commit()  
        
    message['code'] = 200
    message['msg'] = 'sucess'
    return message

