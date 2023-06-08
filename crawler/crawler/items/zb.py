import attrs

from crawler.items.base import BaseItem as _BaseItem
from crawler.util.constant import STOCK_EXCHANGE_TYPE, ZB_STAGE, ZB_FILE_TYPE_OF_PROCESS, ZB_FILE_TYPE_OF_AUDIT
from crawler.util import util


class BaseItem(_BaseItem):
    stock_exchange_type: int = attrs.field(default = STOCK_EXCHANGE_TYPE.SH_ZB.value) # 上市交易所
    @property
    def stock_exchange_type_desc(self):
        print('stock_exchange_type', self.stock_exchange_type)
        return STOCK_EXCHANGE_TYPE(self.stock_exchange_type).desc if self.stock_exchange_type else ''
    pass

@attrs.define
class ZBIPOItem(BaseItem): 

    project_id: str = attrs.field(default = '', metadata={'source': 'company_name'}) # 项目id
    company_id: str = attrs.field(default = '', metadata={'source': 'company_name'}) # IPO公司id

    company_name:  str = attrs.field(default = '', metadata={'source': 'company_name'}) # 公司名称
    

    total_fund_rasing : float = attrs.field(default = 0.0, converter=float) # 募集金额（单位：亿）
    
    issue_market_desc: str = attrs.field(default = '',  metadata={'source': 'issue_market_desc'}) # 发行交易所,创业板是16
    @property
    def issue_market(self):
        result = None
        for stage in list(STOCK_EXCHANGE_TYPE):
            if stage.desc == self.issue_market_desc:
                result = stage.value
        return result

    stage_name : str = attrs.field(default = '', metadata={'source': 'stage_name'}) # 所处阶段
    
    # 项目所处阶段
    @property
    def stage(self):
        result = None
        for stage in list(ZB_STAGE):
            if stage.desc == self.stage_name:
                result = stage.value
        return result
        

    csrc_code : str = attrs.field(default = '') # 证监会分类代码
    csrc_desc : str = attrs.field(default = '') # 证监会分类代码说明

    # 保荐机构
    
    sponsor_id: str = attrs.field(default = '', metadata={'source': 'sponsor_name'})

    sponsor_name: str = attrs.field(default = '', metadata={'source': 'sponsor_name'})
    
    sponsor_code: str = attrs.field(default = '', metadata={'source': 'sponsor_name'})

    
    update_date : str = attrs.field(default = '', metadata={'source': 'update_date'}) #更新时间
    create_date : str = attrs.field(default = '', metadata={'source': 'create_date'}) #公司发起申请时间

    update_time: int = attrs.field(default = None, converter = util.convert_time, metadata={'source': 'update_date'})
    create_time: int = attrs.field(default = None, converter = util.convert_time, metadata={'source': 'create_date'})
    
    # 招股说明书url，用于下载解析pdf出募集资金
    file_url: str = attrs.field(default = '',  metadata={'source': 'file_url'})

    # 招股说明书文件名
    file_name: str = attrs.field(default = '', metadata={'source': 'file_name'})
    pass

@attrs.define
class ZBFileItem(BaseItem):
        
    # 文件id
    file_id:  str = attrs.field(default = '', metadata={'source': 'file_name'})
    
    # 文件名
    file_name: str = attrs.field(default = '', metadata={'source': 'file_name'})
    
    
    file_ext: str = attrs.field(default = '', metadata={'source': 'file_ext'})

    # 文件url
    file_url: str = attrs.field(default = '',  metadata={'source': 'file_url'})


    # 上传时间/更新时间
    publish_time: int = attrs.field(default = None, converter = util.convert_time, metadata={'source': 'publish_date'})

    # 上传时间/更新时间
    publish_date: str = attrs.field(default = '', metadata={'source': 'publish_date'})

    
    file_type_of_process_desc: str = attrs.field(default = '', metadata={'source': 'file_type_of_process_desc'})

    file_type_of_audit_desc: str = attrs.field(default = '', metadata={'source': 'file_type_of_audit_desc'})

    # 文件所属进程类型，说明文件所属进度节点
    @property
    def file_type_of_process(self):
        result_type = None
        for stage in list(ZB_FILE_TYPE_OF_PROCESS):
            
            if stage.desc == self.file_type_of_process_desc:
                result_type = stage.value
        return result_type

    # 文件所属提交类型，标识提交给权力机构审核的文件
    @property
    def file_type_of_audit(self):
        result_type = None
        for stage in list(ZB_FILE_TYPE_OF_AUDIT):
            if stage.desc == self.file_type_of_audit_desc:
                result_type = stage.value
        return result_type


    # 归属项目id
    project_id: str = attrs.field(default = '', metadata={'source': 'company_name'})
    # 公司id
    company_id: str = attrs.field(default = '', metadata={'source': 'company_name'})
    # 公司名
    company_name: str = attrs.field(default = '', metadata={'source': 'company_name'})
    
    
    stage_name : str = attrs.field(default = '', metadata={'source': 'stage_name'}) # 所处阶段
    
    # 文件所属阶段
    @property
    def stage(self):
        result = None
        for stage in list(ZB_STAGE):
            if stage.desc == self.stage_name:
                result = stage.value
        return result
    
    pass

"""@Return 定义创业板公司里程碑数据
"""
@attrs.define
class ZBCompanyProcessItem(BaseItem):
    
    # def __init__(self):
    #     self.id = str(uuid.uuid1())
    project_id: str = attrs.field(default = '', metadata={'source': 'company_name'}) # 项目id
    company_id: str = attrs.field(default = '', metadata={'source': 'company_name'}) # IPO公司id
    company_name: str = attrs.field(default = '', metadata={'source': 'company_name'}) # IPO公司名称


    stage_name : str = attrs.field(default = '', metadata={'source': 'stage_name'}) # 所处阶段
    
    # 项目所处阶段
    @property
    def stage(self):
        result = None
        for stage in list(ZB_STAGE):
            if stage.desc == self.stage_name:
                result = stage.value
        return result

    timestamp: int = attrs.field(default = '', converter = util.convert_time, metadata={'source': 'update_date'})
    # 时间
    date : str = attrs.field(default = '',  metadata={'source': 'update_date'}) # 日期

    @property
    def id(self):
        return "%s-%s-%s" %(self.company_id, self.project_id, str(self.stage))
    pass