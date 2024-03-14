# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Computed, DECIMAL, DateTime, Enum, Index, String, text  # noqa: F401
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, SMALLINT, TINYINT
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.orm.base import Mapped  # noqa: F401, F811

Base = declarative_base()


class GraspBlInvbraDtl(Base):
    __tablename__ = 'grasp_bl_invbra_dtl'
    __table_args__ = (
        Index('index_billid', 'sid', 'billid'),
    )

    billid = mapped_column(BIGINT(18), nullable=False, comment='单据号')
    pro_no = mapped_column(BIGINT(18), nullable=False, comment='货物编码')
    pro_name = mapped_column(String(255), nullable=False, comment='货物名称')
    spec = mapped_column(String(255), nullable=False, server_default=text("''"), comment='货物规格')
    units = mapped_column(String(255), nullable=False, server_default=text("''"), comment='单位')
    qty_sale = mapped_column(DECIMAL(18, 3), nullable=False, comment='数量')
    price_sale_excl = mapped_column(DECIMAL(18, 12), nullable=False, comment='销售未税价')
    amt_excl = mapped_column(DECIMAL(18, 2), nullable=False, comment='未税金额')
    tax = mapped_column(DECIMAL(18, 2), nullable=False, comment='税额')
    rat_tax_sale = mapped_column(TINYINT(4), nullable=False, comment='销售税率')
    flow_no = mapped_column(INTEGER(4), nullable=False, server_default=text("'0'"), comment='排序')
    remark = mapped_column(String(255), nullable=False, server_default=text("''"), comment='备注')
    sid = mapped_column(INTEGER(1), nullable=False, server_default=text("'0'"), comment='数据标识 0不生效 1生产 2测试 3 作废')
    id = mapped_column(BIGINT(20), primary_key=True, comment='序号')
    ldt = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='最后更新日期')


class GraspBlInvbraHdr(Base):
    __tablename__ = 'grasp_bl_invbra_hdr'
    __table_args__ = (
        Index('index_billid', 'billid', unique=True),
    )

    billid = mapped_column(BIGINT(18), nullable=False, comment='单据号 门店发票1411  6位日期 4位流水 1位星期(流水支持自 扩)')
    bltid = mapped_column(TINYINT(4), nullable=False, server_default=text("'0'"), comment='单据类型 0初始 1销售 -1退货')
    blsid = mapped_column(TINYINT(4), nullable=False, server_default=text("'0'"), comment='单据状态 0初始 1未确认 2制单 确认 3已确认 4已驳回 5审批中 6已完成 7已关单 8已转单 9已作废 ')
    supplier_no = mapped_column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='销售方 大仓')
    supplier_name = mapped_column(String(255), nullable=False, server_default=text("''"), comment='销售方名称')
    buyer_no = mapped_column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='购买方 门店')
    buyer_name = mapped_column(String(255), nullable=False, server_default=text("''"), comment='购买方名称')
    out_storage_no = mapped_column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='发货仓 减库存')
    in_storage_no = mapped_column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='收货仓 加库存 暂无')
    fi_addr = mapped_column(String(255), nullable=False, server_default=text("''"), comment='地址')
    fi_tel = mapped_column(String(255), nullable=False, server_default=text("''"), comment='电话')
    buyer_tax_code = mapped_column(String(255), nullable=False, server_default=text("''"), comment='买方税号')
    accounts_bank = mapped_column(String(255), nullable=False, server_default=text("''"), comment='开户银行')
    accounts_code = mapped_column(String(255), nullable=False, server_default=text("''"), comment='开户帐号')
    inv_id = mapped_column(String(255), nullable=False, server_default=text("''"), comment='发票代码')
    inv_no = mapped_column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='发票号码')
    inv_name = mapped_column(String(255), nullable=False, server_default=text("''"), comment='发票名称')
    remark = mapped_column(String(255), nullable=False, server_default=text("''"), comment='备注')
    code_from = mapped_column(String(255), nullable=False, server_default=text("'0'"), comment='单据来源代码')
    userid = mapped_column(BIGINT(18), nullable=False, server_default=text("'0'"), comment='用户ID')
    sid = mapped_column(INTEGER(1), nullable=False, server_default=text("'0'"), comment='数据标识 0不生效 1生产 2测试 3 作废')
    id = mapped_column(BIGINT(20), primary_key=True, comment='序号')
    ldt = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='最后更新日')


class GraspBlInvsupDtl(Base):
    __tablename__ = 'grasp_bl_invsup_dtl'
    __table_args__ = (
        Index('index_billid', 'sid', 'billid'),
    )

    billid = mapped_column(BIGINT(18), nullable=False, comment='单据号2位业务标识 6位日期 2位类型 7位流水 1位星期')
    pro_no = mapped_column(BIGINT(18), nullable=False, comment='货物编码')
    pro_name = mapped_column(String(255), nullable=False, comment='货物名称')
    spec = mapped_column(String(255), nullable=False, comment='货物规格')
    units = mapped_column(String(255), nullable=False, comment='单位')
    qty_pur = mapped_column(DECIMAL(18, 3), nullable=False, comment='数量')
    price_pur_excl = mapped_column(DECIMAL(18, 12), nullable=False, comment='采购未税价')
    amt_excl = mapped_column(DECIMAL(18, 2), nullable=False, comment='未税金额')
    tax = mapped_column(DECIMAL(18, 2), nullable=False, comment='税额')
    rat_tax_pur = mapped_column(TINYINT(4), nullable=False, comment='采购税率')
    flow_no = mapped_column(INTEGER(4), nullable=False, comment='排序')
    remark = mapped_column(String(255), nullable=False, server_default=text("''"), comment='备注')
    sid = mapped_column(INTEGER(1), nullable=False, server_default=text("'0'"), comment='数据标识 0不生效 1生产 2测试 3 作废')
    id = mapped_column(BIGINT(20), primary_key=True, comment='序号')
    ldt = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='最后更新时间')


class GraspBlInvsupHdr(Base):
    __tablename__ = 'grasp_bl_invsup_hdr'
    __table_args__ = (
        Index('index_billid', 'billid', unique=True),
        Index('index_idno', 'inv_id', 'inv_no')
    )

    billid = mapped_column(BIGINT(18), nullable=False, comment='单据号2位业务标识 2位类型  6位日期 4位流水 1位星期(流水 支持自扩)')
    bill_code = mapped_column(String(255), nullable=False, server_default=text("''"), comment='客户单号')
    bltid = mapped_column(TINYINT(4), nullable=False, server_default=text("'0'"), comment='单据类型 0初始')
    blsid = mapped_column(TINYINT(4), nullable=False, server_default=text("'0'"), comment='单据状态 0初始 1未确认 2制单 确认 3已确认 4已驳回 5审批中 6已完成 7已关单 8已转单 9已作废 ')
    supplier_no = mapped_column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='供应商ID')
    supplier_name = mapped_column(String(255), nullable=False, server_default=text("''"), comment='供应商名称')
    buyer_no = mapped_column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='购买方ID')
    buyer_name = mapped_column(String(255), nullable=False, server_default=text("''"), comment='购买方名称')
    out_storage_no = mapped_column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='发货仓')
    in_storage_no = mapped_column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='收货仓')
    inv_id = mapped_column(String(255), nullable=False, server_default=text("''"), comment='发票代码')
    inv_no = mapped_column(String(255), nullable=False, server_default=text("''"), comment='发票号码')
    inv_name = mapped_column(String(255), nullable=False, server_default=text("''"), comment='发票名称')
    inv_date = mapped_column(String(255), nullable=False, server_default=text("''"), comment='开票日期')
    check_id = mapped_column(String(255), nullable=False, server_default=text("''"), comment='校验码')
    machine_no = mapped_column(BIGINT(20), nullable=False, comment='机器编号')
    taxpayer_id = mapped_column(String(255), nullable=False, server_default=text("''"), comment='纳税人识别号')
    fi_addr = mapped_column(String(255), nullable=False, server_default=text("''"), comment='地址')
    fi_tel = mapped_column(String(255), nullable=False, server_default=text("''"), comment='地址和电话')
    accounts_bank = mapped_column(String(255), nullable=False, server_default=text("''"), comment='开户行')
    accounts_code = mapped_column(String(255), nullable=False, server_default=text("''"), comment='开户帐号')
    remark = mapped_column(String(255), nullable=False, server_default=text("''"), comment='备注')
    code_from = mapped_column(String(255), nullable=False, server_default=text("'0'"), comment='单据来源')
    userid = mapped_column(BIGINT(18), nullable=False, server_default=text("'0'"), comment='用户ID')
    sid = mapped_column(INTEGER(1), nullable=False, server_default=text("'0'"), comment='数据标识 0不生效 1生产 2测试 3 作废')
    id = mapped_column(BIGINT(20), primary_key=True, comment='序号')
    ldt = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='最近更新时间')
    inv_idno = mapped_column(String(255), Computed('(concat(`inv_id`,`inv_no`))', persisted=False), comment='合并票号')


class GraspBranch(Base):
    __tablename__ = 'grasp_branch'

    sid = mapped_column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='数据标识 0不生效1生效2测试3假 删除')
    cort_no = mapped_column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='公司编码')
    bra_no = mapped_column(INTEGER(11), primary_key=True, server_default=text("'0'"), comment='编码')
    bra_id = mapped_column(String(36), nullable=False, server_default=text("''"), comment='自定义编码')
    bra_name = mapped_column(String(36), nullable=False, server_default=text("''"), comment='名称')
    bra_sname = mapped_column(String(36), nullable=False, server_default=text("''"), comment='简称')
    bra_type = mapped_column(Enum('A', 'B', 'C', 'N', 'DC'), nullable=False, server_default=text("'N'"))
    type_no = mapped_column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='类型')
    status_no = mapped_column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='状态')
    social_credit_code = mapped_column(String(36), nullable=False, server_default=text("''"), comment='统一社会信用码')
    tax_code = mapped_column(String(36), nullable=False, server_default=text("''"), comment='税号')
    accounts_bank = mapped_column(String(36), nullable=False, server_default=text("''"), comment='开户行')
    accounts_code = mapped_column(String(36), nullable=False, server_default=text("''"), comment='开户帐号')
    fi_addr = mapped_column(String(255), nullable=False, server_default=text("''"), comment='注册地址')
    fi_tel = mapped_column(String(36), nullable=False, server_default=text("''"), comment='注册电话')
    total_area = mapped_column(DECIMAL(18, 3), nullable=False, server_default=text("'0.000'"), comment='总面积')
    open_date = mapped_column(String(36), nullable=False, server_default=text("''"), comment='开店日期')
    remark = mapped_column(String(255), nullable=False, server_default=text("''"), comment='备注')


class GraspOnhand(Base):
    __tablename__ = 'grasp_onhand'
    __table_args__ = (
        Index('index_pro', 'sid', 'storage_no', 'pro_no', unique=True),
    )

    storage_no = mapped_column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='收货仓')
    pro_no = mapped_column(BIGINT(18), nullable=False, comment='商品编码')
    pro_name = mapped_column(String(255), nullable=False, comment='商品名称')
    spec = mapped_column(String(255), nullable=False, server_default=text("''"), comment='规格型号')
    units = mapped_column(String(255), nullable=False, server_default=text("''"), comment='单位')
    qty_aval = mapped_column(DECIMAL(18, 3), nullable=False, server_default=text("'0.000'"), comment='可用数量')
    price_pur_last = mapped_column(DECIMAL(18, 6), nullable=False, server_default=text("'0.000000'"), comment='最近采购 单价')
    remark = mapped_column(String(255), nullable=False, server_default=text("''"), comment='备注')
    sid = mapped_column(INTEGER(1), nullable=False, server_default=text("'0'"), comment='数据标识 0不生效 1生产 2测试 3 作废')
    id = mapped_column(BIGINT(20), primary_key=True, comment='序号')
    ldt = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='最后更新时间')


class GraspProduct(Base):
    __tablename__ = 'grasp_product'
    __table_args__ = (
        Index('idx_pro', 'grasp_pro'),
    )

    pro_no = mapped_column(BIGINT(18), primary_key=True, comment='商品编码')
    pro_name = mapped_column(String(128), nullable=False, server_default=text("''"), comment='商品名称')
    spec = mapped_column(String(36), nullable=False, server_default=text("''"), comment='规格')
    units = mapped_column(String(36), nullable=False, server_default=text("''"), comment='单位')
    price_pur_excl = mapped_column(DECIMAL(18, 12), nullable=False, server_default=text("'0.000000000000'"), comment='采购未税价')
    rat_tax_pur = mapped_column(SMALLINT(3), nullable=False, comment='采购税率')
    rat_tax_sale = mapped_column(SMALLINT(3), nullable=False, comment='销售税率')
    remark = mapped_column(String(255), nullable=False, server_default=text("''"), comment='备注')
    sid = mapped_column(TINYINT(4), nullable=False, server_default=text("'0'"), comment='数据标识 0不生效 1生产 2测试 3 作废')
    ldt = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新日期')
    grasp_pro = mapped_column(String(255), Computed('(concat(`pro_name`,`spec`,`units`))', persisted=False), comment='商品')
    price_sale_excl = mapped_column(DECIMAL(18, 12), Computed('((`price_pur_excl` * 1.03))', persisted=False), comment='销售未税价')


class GraspSupplier(Base):
    __tablename__ = 'grasp_supplier'
    __table_args__ = (
        Index('idx_tax_code', 'tax_code'),
    )

    sup_no = mapped_column(BIGINT(18), primary_key=True, comment='供应商编码')
    sup_id = mapped_column(String(36), nullable=False, server_default=text("''"), comment='客户自定码')
    sup_sname = mapped_column(String(36), nullable=False, server_default=text("''"), comment='供应商简称')
    sup_name = mapped_column(String(36), nullable=False, comment='供应商名称')
    fi_addr = mapped_column(String(128), nullable=False, server_default=text("''"), comment='地址')
    fi_tel = mapped_column(String(36), nullable=False, server_default=text("''"), comment='电话')
    social_credit_code = mapped_column(String(36), nullable=False, server_default=text("''"), comment='统一信用码')
    tax_code = mapped_column(String(36), nullable=False, server_default=text("''"), comment='税号')
    accounts_bank = mapped_column(String(64), nullable=False, server_default=text("''"), comment='银行')
    accounts_code = mapped_column(String(36), nullable=False, server_default=text("''"), comment='银行码')
    cort_no = mapped_column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='核算ID')
    remark = mapped_column(String(36), nullable=False, server_default=text("''"), comment='备注')
    sid = mapped_column(TINYINT(4), nullable=False, server_default=text("'0'"), comment='数据标识 0不生效 1生产 2测试 3 作废')
    ldt = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='最后更新时间')


class GraspWba(Base):
    __tablename__ = 'grasp_wba'
    __table_args__ = (
        Index('index_wba', 'sid', 'billid', 'act_no', 'pro_no', unique=True),
    )

    billid = mapped_column(BIGINT(18), nullable=False, comment='单据号2位业务标识 6位日期 2位类型 7位流水 1位星期')
    acc_no = mapped_column(TINYINT(4), nullable=False, server_default=text("'1'"), comment='入账标识 1加 -1减 可负负得正')
    act_no = mapped_column(TINYINT(4), nullable=False, comment='单据动作 0初始 61审核未入账66审核入账 91反审未入账 96反 审入账')
    supplier_no = mapped_column(INTEGER(11), nullable=False, comment='销售方')
    buyer_no = mapped_column(INTEGER(11), nullable=False, comment='购买方')
    out_storage_no = mapped_column(INTEGER(11), nullable=False, comment='发货仓 减少库存')
    in_storage_no = mapped_column(INTEGER(11), nullable=False, comment='收货仓 增加库存')
    pro_no = mapped_column(BIGINT(18), nullable=False, comment='商品编码')
    pro_name = mapped_column(String(255), nullable=False, comment='商品名称')
    spec = mapped_column(String(255), nullable=False, server_default=text("''"), comment='规格型号')
    units = mapped_column(String(255), nullable=False, server_default=text("''"), comment='单位')
    qty = mapped_column(DECIMAL(18, 3), nullable=False, comment='数量')
    price = mapped_column(DECIMAL(18, 12), nullable=False, comment='采购单价')
    amt = mapped_column(DECIMAL(18, 2), nullable=False, comment='金额')
    tax = mapped_column(DECIMAL(18, 2), nullable=False, comment='税额')
    rat_tax = mapped_column(TINYINT(4), nullable=False, comment='税率')
    remark = mapped_column(String(255), nullable=False, server_default=text("''"), comment='备注')
    sid = mapped_column(INTEGER(1), nullable=False, server_default=text("'0'"), comment='数据标识 0不生效 1生产 2测试 3 作废')
    id = mapped_column(BIGINT(20), primary_key=True, comment='序号')
    ldt = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')


# # 连接数据库
# DATABASE_URL = "mysql+pymysql://root:shtm2022@192.168.200.174:3306/grasp"
# engine = create_engine(DATABASE_URL, echo=True)
 
# # 创建会话
# Session = sessionmaker(bind=engine)
# session = Session()
 
# # 创建所有表
# Base.metadata.create_all(engine)