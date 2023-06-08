"""
定义创业板交易所的结构数据
Company 公司
Project 项目
Intermediate 中介机构
Person 人
Milestone里程碑
File 文件
Process 进度

"""

import uuid
import re
import types
import scrapy
import attrs
import attr
import json
from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy.loader import ItemLoader
from dataclasses import dataclass
from pydash import objects
from datetime import datetime


from ..util.constant import STOCK_EXCHANGE_TYPE, INTERMEDIARY_TYPE, SZ_IPO_STAGE, SZ_IPO_FileTypeOfProcess_TO_SZ_IPO_STAGE, SZ_IPO_FileTypeOfAuditEnum, SZ_IPO_FileTypeOfProcessEnum
from crawler.items.base import BaseItem as _BaseItem
from crawler.util import util

def convert_to_int(value):
    result = None
    try:
        result = int(value)
    except:
        result = None
    return result

def convert_time(time_str):
    date_obj = None
    formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%d %H:%M']
    for format in formats:
        if date_obj != None:
            break
        else:
            try:
                date_obj = datetime.strptime(time_str, format)
            except:
                pass
    return int(round(date_obj.timestamp() * 1000)) if date_obj != None else None

class BaseItem(_BaseItem):
    stock_exchange_type: int = attrs.field(default = STOCK_EXCHANGE_TYPE.CYB.value) # 上市交易所
    stock_exchange_type_desc: str = attrs.field(default = STOCK_EXCHANGE_TYPE.CYB.desc) # 上市交易所名称
    pass


"""Return Company
定义交易所的公司数据

"""
@attrs.define
class SZ_IPO_CompanyItem(BaseItem):
    id: str = attrs.field(default = '', metadata={'source': 'entid'})  # 公司唯一标识id
    name : str = attrs.field(default = '', metadata={'source': 'cmpnm'}) # 公司名称
    abbr : str = attrs.field(default = '', metadata={'source': 'cmpsnm'}) # 公司简称
    
    code : str = attrs.field(default = '', metadata={'source': 'cmpcode'}) # 公司证券代码

    csrc_company_type : int = attrs.field(default = INTERMEDIARY_TYPE.NORMAL.value) # 在证监会领域内的公司类型
   
    csrc_code : str = attrs.field(default = '', metadata={'source': ''}) # 证监会分类代码
    csrc_desc : str = attrs.field(default = '', metadata={'source': 'csrcind'}) # 证监会分类代码说明
    
    province : str = attrs.field(default = '', metadata={'source': 'regloc'}) # 省份

    city : str = attrs.field(default = '') # 城市

    phone : str = attrs.field(default = '') # 电话
    website : str = attrs.field(default = '') # 站点 
    email : str = attrs.field(default = '') # email

    # 证监会分类代码父级
    @property
    def csrc_parent_code(self):
        return self.csrc_code[0] if self.csrc_code != '' else ''

    # 公司地址
    @property
    def loc(self):
        if self.province == '境外':
            return self.province
        return self.province + ("-%s" % (self.city) if self.province and self.city else '')

    pass 


"""@Return 定义IPO列表数据
"""
@attrs.define
class SZ_IPO_Item(BaseItem):
    
    def build_intermediary_convert(type):
        def intermediary_convert(list = []):
            intermediary_list = [item for i, item in enumerate(list) if item['i_intermediaryType'] == type]
            if len(intermediary_list) > 0:
                [intermediary, *other] = intermediary_list
                return intermediary
            else:
                return ''
        return intermediary_convert 


    project_id: str = attrs.field(default = '', metadata={'source': 'prjid'}) # 项目id
    company_id: str = attrs.field(default = '') # IPO公司id

    company_name:  str = attrs.field(default = '', metadata={'source': 'cmpnm'}) # 公司名称
    
    issue_market : int = attrs.field(default = None, converter=convert_to_int,  metadata={'source': 'boardCode'}) # 发行交易所,创业板是16

    # board_code : int = attrs.field(default = None, converter=convert_to_int, metadata={'source': 'boardCode'}) # IPO板块
    issue_market_desc : str = attrs.field(default = None, metadata={'source': 'boardName'}) # IPO板块名称

    total_fund_rasing : float = attrs.field(default = 0.0, converter=float, metadata={'source': 'maramt'}) # 募集金额（单位：亿）
    
    # 项目所处流程
    stage : str = attrs.field(default = '', metadata={'source': 'stage'}) # 所处阶段
    
    @property
    def stage_name(self):
        return SZ_IPO_STAGE(self.stage).desc if self.stage and SZ_IPO_STAGE(self.stage) else ''
        
    stage_status : str = attrs.field(default = '', metadata={'source': 'prjstatus'}) # 阶段状态
    
    stage_status_name: str = attrs.field(default = '', metadata={'source': 'prjst'}) # 阶段状态

    biz_type : int = attrs.field(default = None, metadata={'source': 'biztype'}) # 业务类型

    

    csrc_code : str = attrs.field(default = '') # 证监会分类代码
    csrc_desc : str = attrs.field(default = '', metadata={'source': 'csrcind'}) # 证监会分类代码说明

    # 律师事务所
    
    law_office_id: int = attrs.field(default = None, metadata={'source': 'lawfm'})

    law_office_name: str = attrs.field(default = None, metadata={'source': 'lawfm'})

    
    # 保荐机构，律师事务所，会计事务所，用了三种方式获取数据
    # 保荐机构
    
    sponsor_id: str = attrs.field(default = '', metadata={'source': 'sprinst'})

    sponsor_name: str = attrs.field(default = '', metadata={'source': 'sprinst'})
    
    sponsor_code: str = attrs.field(default = '', metadata={'source': 'sprcd'})

    # 次承销商（协助保荐机构）
    sub_sponsor_id: str = attrs.field(default = '', metadata={'source': 'jsprinst'})

    sub_sponsor_name: str = attrs.field(default = '', metadata={'source': 'jsprinst'})
    
    sub_sponsor_code: str = attrs.field(default = '', metadata={'source': 'jsprcd'})

    #sponsor_signatory_id : str = attrs.field(default = '')

    # 会计事务所
    accounting_firm_id : str = attrs.field(default = '',
        metadata={'source': 'acctfm'}
    )
    # 会计事务所
    accounting_firm_name : str = attrs.field(default = '',
        metadata={'source': 'acctfm'}
    )
    #accounting_firm_signatory_id : str = attrs.field(default = '')

    # 资信评级
    asset_evaluation_institute_id: str = attrs.field(default = '',
        metadata={'source': 'evalinst'}
    )
    # 资信评级
    asset_evaluation_institute_name: str = attrs.field(default = '',
        metadata={'source': 'evalinst'}
    )

    # 资产评估机构
    rating_agency_id : str = ''
    # 资产评估机构
    rating_agency_name : str = ''
    

    accept_apply_date : str = attrs.field(default = '', metadata={'source': 'acptdt'}) #交易所受理时间
    update_date : str = attrs.field(default = '', metadata={'source': 'updtdt'}) #更新时间
    create_date : str = attrs.field(default = '', metadata={'source': 'acptdt'}) #公司发起申请时间

    accept_apply_time: int = attrs.field(default = None, converter = convert_time, metadata={'source': 'acptdt'})
    update_time: int = attrs.field(default = None, converter = convert_time, metadata={'source': 'updtdt'})
    create_time: int = attrs.field(default = None, converter = convert_time, metadata={'source': 'acptdt'})
    
     # 人员信息存到另一个字段中
    # signing_attorney_id : str = attrs.field(default = '')
    pass



"""@Return 定义创业板中介机构数据
"""
@attrs.define
class SZ_IPO_IntermediaryItem(BaseItem):
    # 项目id
    project_id: str = attrs.field(default = '', metadata={'source': 'prjid'}) 
    
    
    # 中介机构id，需要找到数据库里是否存在这个id
    intermediary_id : str = attrs.field(default = '', metadata={'source': 'name'})
    
    # 中介类型
    type: int = attrs.field(default=None, metadata={'source': 'type'})
    # 中介机构名称
    name: str = attrs.field(default='', metadata={'source': 'name'})
   
   
    # 中介顺序（科创板返回的数据）
    intermediary_order: int = attrs.field(default = None) 
    pass


"""@Return 定义创业板中介机构人员数据
"""
@attrs.define
class SZ_IPO_IntermediaryPersonItem(BaseItem):
    # 项目id
    project_id: str = attrs.field(default = '', metadata={'source': 'prjid'}) 
    # 中介机构id
    intermediary_id : str = attrs.field(default = '', metadata={'source': 'intermediary_id'}) 
    
    # 人员id，要找到person数据库里是否存在这个id
    id : str = attrs.field(default='', metadata={'source': 'personName'})
    # 人员姓名
    name: str = attrs.field(default='', metadata={'source': 'personName'})
    
    # 任职职位类型
    job_type: int = attrs.field(default=None)

    # 任职职位名称
    job_title: str = attrs.field(default='')  
    pass

@attrs.define
class SZ_IPO_FileItem(BaseItem):
    def url(value):
        return "https://reportdocs.szse.cn%s" % (value)
        
    # 文件id
    file_id:  str = attrs.field(default = '', metadata={'source': 'dfid'})
    
    _file_name: str = attrs.field(default = '', metadata={'source': 'dfnm'})
    
    # 文件名
    _file_ext: str = attrs.field(default = '', metadata={'source': 'dfext'})

    # 文件名
    @property
    def file_name(self):
        if self._file_ext:
            if self._file_ext in self._file_name:
                return self._file_name
            else:
                return "%s.%s" % (self._file_name, self._file_ext)
        else:
            return "%s.pdf" % (self._file_name) if ".pdf" not in self._file_name else self._file_name
    

    # 文件url
    file_url: str = attrs.field(default = '', converter = url, metadata={'source': 'dfpth'})
    # 文件大小
    file_size: int = attrs.field(default = 0)

    # 上传时间/更新时间
    publish_time: int = attrs.field(default = None, converter = convert_time, metadata={'source': 'ddtime'})

    # 上传时间/更新时间
    publish_date: str = attrs.field(default = '', metadata={'source': 'ddtime'})

    # 文件所属进程类型，说明文件所属进度节点
    file_type_of_process: int = attrs.field(default = -1, converter=convert_to_int, metadata={'source': 'dtyp'})

    # 文件所属提交类型，标识提交给权力机构审核的文件
    file_type_of_audit: int = attrs.field(default = -1, converter=convert_to_int, metadata={'source': 'matcat'})

    @property
    def file_type_of_process_desc(self):
        return SZ_IPO_FileTypeOfProcessEnum(self.file_type_of_process).desc if self.file_type_of_process else ''

    @property
    def file_type_of_audit_desc(self):
        return SZ_IPO_FileTypeOfAuditEnum(self.file_type_of_audit).desc if self.file_type_of_audit else ''


    # 归属项目id
    project_id: str = attrs.field(default = '', metadata={'source': 'prjid'})
    # 公司id
    company_id: str = attrs.field(default = '')
    # 公司名
    company_name: str = attrs.field(default = '', metadata={'source': 'cmpnm'})
    
    # 文件所属阶段
    @property
    def stage(self):
        # 文件类型到文件所属阶段的映射
        return SZ_IPO_FileTypeOfProcess_TO_SZ_IPO_STAGE[self.file_type_of_process] if self.file_type_of_process in SZ_IPO_FileTypeOfProcess_TO_SZ_IPO_STAGE.keys() else ''
    

    @property
    def stage_name(self):
        if self.stage and SZ_IPO_STAGE(self.stage):
            return SZ_IPO_STAGE(self.stage).desc
    
    pass


"""@Return 定义创业板公司里程碑数据
"""
@attrs.define
class SZ_IPO_CompanyMilestoneItem(BaseItem):
    
    # def __init__(self):
    #     self.id = str(uuid.uuid1())
    project_id: str = attrs.field(default = '', metadata={'source': 'stockAuditNum'}) # 项目id
    company_id: str = attrs.field(default = '') # IPO公司id
    company_name: str = attrs.field(default = '') # IPO公司名称

    stage_status : int = attrs.field(default = None, metadata={'source': 'value'}) # 阶段状态

    stage_status_name : str = attrs.field(default = '', metadata={'source': 'caption'}) # 阶段状态

    # 项目所处流程
    @property
    def stage(self):
        # 特殊逻辑，因为创业板详情返回的数据可能和列表中的数据stage的枚举值不一致。比如终止这个枚举
        if self.stage_status_name == '终止':
            return SZ_IPO_STAGE.END.value
        else:
            for name, member in SZ_IPO_STAGE.__members__.items():
                status = member.status
                if any(s['value'] == self.stage_status for s in status):
                    return member.value

    @property
    def stage_name(self):
        if self.stage and SZ_IPO_STAGE(self.stage):
            return SZ_IPO_STAGE(self.stage).desc

    timestamp: int = attrs.field(default = None, converter = convert_time, metadata={'source': 'date'})
    # 时间
    date : str = attrs.field(default = '', metadata={'source': 'date'}) # 日期

    @property
    def id(self):
        return "%s-%s-%s-%s" %(self.company_id, self.project_id, str(self.stage),str(self.stage_status))
    pass


"""@Return 定义创业板公司其他披露消息数据
"""
@attrs.define
class SZ_IPO_CompanyOtherItem(BaseItem):
    @property
    def id(self):
        return "%s-%s" %(self.project_id, self.company_id)
    
    project_id: str = attrs.field(default = '')
    company_id: str = attrs.field(default = '')
    company_name: str = attrs.field(default = '')
    
    reason: str = attrs.field(default = '', metadata={'source': 'reason'})

    timestamp: int = attrs.field(default = None, converter = convert_time, metadata={'source': 'date'})

    # 时间
    date : str = attrs.field(default = '', metadata={'source': 'date'}) # 日期



"""@Return 定义创业板公司原始数据,存储原始数据，用于后续解析及分析比对，存于mongodb，不搞关系型那套
而只有在文件、进程状态更新时，对其进行全部更新
"""
@attrs.define
class SZ_IPO_CompanySourceItem(BaseItem):
    project_id: str = attrs.field(default = '', metadata={'source': 'projectId'})
    ipo_result: str = attrs.field(default = '', metadata={'source': 'ipoResult'})
    detail_result: str = attrs.field(default = '', metadata={'source': 'detailResult'})
    pass
