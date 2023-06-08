"""
定义科创板交易所的结构数据
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


from ..util.constant import STOCK_BUSINESS_TYPE, STOCK_EXCHANGE_TYPE, INTERMEDIARY_TYPE, SH_IPO_STAGE, SH_STOCK_TYPE, SH_IPO_FileType_Enum, SH_ZRZ_BUSINESS_TYPE, SH_ZRZ_STAGE
from crawler.items.base import BaseItem as _BaseItem
from crawler.util import util

def stage_status_convert(self, retrive_dict = {}): 
        #print('KCB_STAGE.STATUS', KCB_STAGE.STATUS)
    result = None
    if self.stage == SH_IPO_STAGE.MUNICIPAL_PARTY_COMMITTEE.value:
        result = retrive_dict['commitiResult']
    if self.stage == SH_IPO_STAGE.REGIST_RESULT.value:
        result = retrive_dict['registeResult']
    if self.stage == SH_IPO_STAGE.SUSPEND.value:
        result = retrive_dict['suspendStatus']
    if result == '':
        return None
    return result

def convert_time(time_str, format = ''):
    date_obj = None
    if format != '': 
        try:
            date_obj = datetime.strptime(time_str, format)
        except:
            pass
    else:
        try:
            date_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        except:
            try:
                date_obj = datetime.strptime(time_str, '%Y%m%d%H%M%S')
            except:
                try:
                    date_obj = datetime.strptime(time_str, '%Y-%m-%d')
                except:
                    pass
    return int(round(date_obj.timestamp() * 1000)) if date_obj != None else None

def convert_to_int(value):
    result = None
    try:
        result = int(value)
    except:
        result = None
    return result

def stage_name(self, STAGE = SH_IPO_STAGE):
    return STAGE(self.stage).desc if self.stage and STAGE(self.stage) else ''

def stage_status_name(self, STAGE = SH_IPO_STAGE):
    result = ''
        
    if self.stage_status:
        for name, member in STAGE.__members__.items():
            if self.stage == member.value:
                status = member.status
                result_status = [s_status for i, s_status in enumerate(status) if str(s_status['value']) == str(self.stage_status)]
                if len(result_status) > 0:
                    result_status = result_status[0]
                    result = result_status['name']
    return result

class BaseItem(_BaseItem):
    stock_exchange_type: int = attrs.field(default = STOCK_EXCHANGE_TYPE.CYB.value) # 上市交易所
    stock_exchange_type_desc: str = attrs.field(default = STOCK_EXCHANGE_TYPE.CYB.desc) # 上市交易所名称
    pass


"""Return Company
定义交易所的公司数据

"""
@attrs.define
class CompanyItem(BaseItem):
    # TODO: default设置为uuid.uuid1(),则所有companyItem的id都是一样的
    id: str = attrs.field(default = str(uuid.uuid1()), metadata={'source': 'OPERATION_SEQ'})  # 公司唯一标识id
    name : str = attrs.field(default = '', metadata={'source': 'stockAuditName'}) # 公司名称
    abbr : str = attrs.field(default = '', metadata={'source': 'stockIssuer.0.s_issueCompanyAbbrName'}) # 公司简称
    
    code : str = attrs.field(default = '', metadata={'source': 'stockIssuer.0.s_companyCode'}) # 公司证券代码

    csrc_company_type : int = attrs.field(default = INTERMEDIARY_TYPE.NORMAL.value) # 在证监会领域内的公司类型
   
    csrc_code : str = attrs.field(default = '', metadata={'source': 'stockIssuer.0.s_csrcCode'}) # 证监会分类代码
    csrc_desc : str = attrs.field(default = '', metadata={'source': 'stockIssuer.0.s_csrcCodeDesc'}) # 证监会分类代码说明
    
    province : str = attrs.field(default = '', metadata={'source': 'stockIssuer.0.s_province'}) # 省份

    city : str = attrs.field(default = '', metadata={'source': 'stockIssuer.0.s_areaNameDesc'}) # 城市

    phone : str = attrs.field(default = '') # 电话
    website : str = attrs.field(default = '') # 站点 
    email : str = attrs.field(default = '') # email

    # 证监会分类代码父级
    @property
    def csrc_parent_code(self):
        if self.csrc_code == None:
            return ''
        return self.csrc_code[0] if self.csrc_code != '' else ''

    # 公司地址
    @property
    def loc(self):
        if self.province == '境外':
            return self.province
        return self.province + '-' + self.city if self.province and self.city else ''

    pass 

"""@Return 高管人员表

"""
@attrs.define
class CompanyManagerItem(BaseItem):
    company_id: str = attrs.field(default = '')  # 公司唯一标识id
    company_name: str = attrs.field(default = '', metadata={'source': 's_issueCompanyFullName'})  # 公司名
    
    id: str = attrs.field(default = str(uuid.uuid1()), metadata={'source': 's_personId'})  # 个人id
    
    # 公司唯一标识id
    name: str = attrs.field(default = '', metadata={'source': 's_personName'})

    # 任职职位名称
    job_title: str = attrs.field(default='', metadata={'source': 's_jobTitle'})  

    # 任职职位类型
    @property
    def job_type(self):
        # return JOB_TYPE_DICT[self.job_title] if self.job_title and self.job_title in JOB_TYPE_DICT.keys() else ''
        return ''
    pass

"""Return Company
定义交易所的中介机构数据

"""
@attrs.define
class IntermediaryItem(BaseItem):
    id: str = attrs.field(default = '', metadata={'source': 'i_intermediaryId'})  # 公司唯一标识id
    name : str = attrs.field(default = '', metadata={'source': 'i_intermediaryName'}) # 公司名称
    abbr : str = attrs.field(default = '', metadata={'source': 'i_intermediaryAbbrName'}) # 公司简称
    
    code : str = attrs.field(default = '') # 公司证券代码

    csrc_company_type : int = attrs.field(default = None, metadata={'source': 'i_intermediaryType'}) # 在证监会领域内的公司类型
   
    csrc_code : str = attrs.field(default = '') # 证监会分类代码
    csrc_desc : str = attrs.field(default = '') # 证监会分类代码说明
    
    province : str = attrs.field(default = '') # 省份

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
        return self.province + '-' + self.city if self.province and self.city else ''

    pass 

# """Return Company
# 定义交易所的中介机构高管人员数据

# """
# @attrs.define
# class IntermediaryManagerItem(CompanyManagerItem):
#     # 中介机构id
#     intermediaty_id: str = attrs.field(default='')

#     id: str = attrs.field(default = str(uuid.uuid1()))  # 个人id
    
#     # 公司唯一标识id
#     name: str = attrs.field(default = '')

#     # 任职职位类型
#     job_type: int = attrs.field(default=None)

#     # 任职职位名称
#     job_title: str = attrs.field(default='')  


"""@Return 定义IPO列表数据
"""
@attrs.define
class SH_IPO_Item(BaseItem):
    def stage_status_convert(self, retrive_dict = {}): 
        return stage_status_convert(self, retrive_dict)
    
    def build_intermediary_convert(type):
        def intermediary_convert(list = []):
            intermediary_list = [item for i, item in enumerate(list) if item['i_intermediaryType'] == type]
            if len(intermediary_list) > 0:
                [intermediary, *other] = intermediary_list
                return intermediary
            else:
                return ''
        return intermediary_convert 


    project_id: str = attrs.field(default = '', metadata={'source': 'stockAuditNum'}) # 项目id
    company_id: str = attrs.field(default = '') # IPO公司id

    company_name:  str = attrs.field(default = '', metadata={'source': 'stockAuditName'}) # 公司名称
    
    issue_market : int = attrs.field(default = None, metadata={'source': 'issueMarketType'}) # 发行交易所

    @property
    def issue_market_desc(self):
        return SH_STOCK_TYPE(self.issue_market).desc if self.issue_market and SH_STOCK_TYPE(self.issue_market) else ''

    stock_business_type: int = attrs.field(default = STOCK_BUSINESS_TYPE.IPO.value) 
    stock_business_type_desc: str = attrs.field(default = STOCK_BUSINESS_TYPE.IPO.desc)

    total_fund_rasing : float = attrs.field(default = None, metadata={'source': 'planIssueCapital'}) # 募集金额（单位：亿）
    
    # 项目所处流程
    stage : int = attrs.field(default = None, metadata={'source': 'currStatus'}) # 所处阶段
    
    @property
    def stage_name(self):
        return stage_name(self)

    stage_status : int = attrs.field(default = None, metadata={'source': stage_status_convert}) # 阶段状态
    
    @property
    def stage_status_name(self):
        return stage_status_name(self)
        

    biz_type : int = attrs.field(default = None, metadata={'source': 'collectType'}) # 业务类型

    csrc_code : str = attrs.field(default = '', metadata={'source': 'stockIssuer.0.s_csrcCode'}) # 证监会分类代码
    csrc_desc : str = attrs.field(default = '', metadata={'source': 'stockIssuer.0.s_csrcCodeDesc'}) # 证监会分类代码说明

    # 律师事务所
    _law_office: dict = attrs.field(
        default={},
        metadata={'source': 'intermediary#{ "rule": "i_intermediaryType=%s"}'%(INTERMEDIARY_TYPE.LAW_FIRM.value)}
    )
    
    @property
    def law_office_id(self):
        return self._law_office['i_intermediaryId']
    
    @property
    def law_office_name(self):
        return self._law_office['i_intermediaryName']
    
    # 保荐机构，律师事务所，会计事务所，用了三种方式获取数据
    # 保荐机构
    _sponsor: dict = attrs.field(
        default={},
        converter=build_intermediary_convert(type = INTERMEDIARY_TYPE.SPONSOR.value),
        metadata={'source': 'intermediary'}
    )

    @property
    def sponsor_id(self):
        return self._sponsor['i_intermediaryId']
    
    @property
    def sponsor_name(self):
        return self._sponsor['i_intermediaryName']
    

    #sponsor_signatory_id : str = attrs.field(default = '')

    # 会计事务所
    accounting_firm_id : str = attrs.field(default = '',
        # 自定义格式
        metadata={'source': 'intermediary#{ "rule": "i_intermediaryType=%s", "path": "i_intermediaryId"}'%(INTERMEDIARY_TYPE.ACCOUNTING_FIRM.value)}
    )
    # 会计事务所
    accounting_firm_name : str = attrs.field(default = '',
        # 自定义格式
        metadata={'source': 'intermediary#{ "rule": "i_intermediaryType=%s", "path": "i_intermediaryName"}'%(INTERMEDIARY_TYPE.ACCOUNTING_FIRM.value)}
    )
    #accounting_firm_signatory_id : str = attrs.field(default = '')

    # 律师事务所
    _rating_agency: dict = attrs.field(
        default={},
        metadata={'source': 'intermediary#{ "rule": "i_intermediaryType=%s"}'%(INTERMEDIARY_TYPE.RATING_AGENCY.value)}
    )
    # 是否有更好的写法
    @property
    def rating_agency_id(self):
        return self._rating_agency['i_intermediaryId'] if 'i_intermediaryId' in self._rating_agency.keys() else ''
    
    @property
    def rating_agency_name(self):
        return self._rating_agency['i_intermediaryName'] if 'i_intermediaryName' in self._rating_agency.keys() else ''

    # 资产评估机构
    _asset_evaluation_institute: dict = attrs.field(
        default={},
        metadata={'source': 'intermediary#{ "rule": "i_intermediaryType=%s"}'%(INTERMEDIARY_TYPE.ASSET_EVALUATION_INSTITUTE.value)}
    )
    # 是否有更好的写法
    @property
    def asset_evaluation_institute_id(self):
        return self._asset_evaluation_institute['i_intermediaryId'] if 'i_intermediaryId' in self._asset_evaluation_institute.keys() else ''
    
    @property
    def asset_evaluation_institute_name(self):
        return self._asset_evaluation_institute['i_intermediaryName'] if 'i_intermediaryName' in self._asset_evaluation_institute.keys() else ''


    accept_apply_date : str = attrs.field(default = '', metadata={'source': 'auditApplyDate'}) #交易所受理时间
    accept_apply_time: int = attrs.field(default = None, converter = convert_time, metadata={'source': 'auditApplyDate'})
    
    update_date : str = attrs.field(default = '', metadata={'source': 'updateDate'}) #更新时间
    update_time: int = attrs.field(default = None, converter = convert_time, metadata={'source': 'updateDate'})

    create_date : str = attrs.field(default = '', metadata={'source': 'createTime'}) #公司发起申请时间
    create_time: int = attrs.field(default = None, converter = convert_time, metadata={'source': 'createTime'})
     # 人员信息存到另一个字段中
    # signing_attorney_id : str = attrs.field(default = '')
    pass



"""@Return 定义科创板中介机构数据
"""
@attrs.define
class SH_IPO_IntermediaryItem(BaseItem):
    # 项目id
    project_id: str = attrs.field(default = '', metadata={'source': 'auditId'}) 
    
    business_type: str = attrs.field(default = '', metadata={'source': 'auditId'})
    
    # 中介机构id
    intermediary_id : str = attrs.field(default = '', metadata={'source': 'i_intermediaryId'}) 
    
    # 中介类型
    type: int = attrs.field(default=None, metadata={'source': 'i_intermediaryType'})
    # 中介机构名称
    name: str = attrs.field(default='', metadata={'source': 'i_intermediaryName'})
   
   
    # 中介顺序（科创板返回的数据）
    intermediary_order: int = attrs.field(default = None, converter = convert_to_int, metadata={'source': 'i_intermediaryOrder'}) 
    pass



"""@Return 定义科创板中介人员
"""
@attrs.define
class SH_IPO_IntermediaryPersonItem(BaseItem):
    # 项目id
    project_id: str = attrs.field(default = '', metadata={'source': 'auditId'}) 
    # 中介机构id
    intermediary_id : str = attrs.field(default = '', metadata={'source': 'i_intermediaryId'}) 
    
    # 人员id
    id : str = attrs.field(default='', metadata={'source': 'i_p_personId'})
    # 人员姓名
    name: str = attrs.field(default='', metadata={'source': 'i_p_personName'})
    
    # 任职职位类型
    job_type: int = attrs.field(default=None, metadata={'source': 'i_p_jobType'})

    # 任职职位名称
    job_title: str = attrs.field(default='', metadata={'source': 'i_p_jobTitle'})  
    pass


"""@Return 定义科创板公司里程碑数据
"""
@attrs.define
class SH_IPO_CompanyMilestoneItem(BaseItem):
    id: str = attrs.field(default = '', metadata={'source': 'auditItemId'}) # 条目id
    project_id: str = attrs.field(default = '', metadata={'source': 'stockAuditNum'}) # 项目id
    company_id: str = attrs.field(default = '') # IPO公司id
    company_name: str = attrs.field(default = '') # IPO公司名称

    def stage_status_convert(self, retrive_dict = {}): 
        return stage_status_convert(self, retrive_dict)
    
    # 项目所处流程
    stage : int = attrs.field(default = None, metadata={'source': 'auditStatus'}) # 所处阶段
    
    @property
    def stage_name(self):
        return stage_name(self)

    stage_status : int = attrs.field(default = None, metadata={'source': stage_status_convert}) # 阶段状态
    
    @property
    def stage_status_name(self):
        return stage_status_name(self)

    timestamp: int = attrs.field(default = None, converter = convert_time, metadata={'source': 'timesave|qianDate|publishDate'})
    # 时间
    date : str = attrs.field(default = '', metadata={'source': 'timesave|qianDate|publishDate'}) # 日期

    pass

"""@Return 定义科创板公司进程数据
"""
@attrs.define
class SH_IPO_CompanyProcessItem(SH_IPO_CompanyMilestoneItem):
    @property
    def stage_name(self):
        return stage_name(self)
    
    @property
    def stage_status_name(self):
        return stage_status_name(self)

    reason: str = attrs.field(default = '', metadata={'source': 'reasonDesc'})

    pass


"""@Return 定义科创板的文件item
"""
@attrs.define
class SH_IPO_FileItem(BaseItem):
    def url(value):
        return "http://kcb.sse.com.cn%s" % (value)

    def file_ext(value):
        return "%s.pdf" % (value)
    # 文件id
    file_id:  str = attrs.field(default = '', metadata={'source': 'fileId'})
    # 文件名
    file_name: str = attrs.field(default = '', converter=file_ext, metadata={'source': 'fileTitle'})
   
    # 文件url
    file_url: str = attrs.field(default = '', converter = url, metadata={'source': 'filePath'})
    # 文件大小
    file_size: int = attrs.field(default = '', metadata={'source': 'fileSize'})

    # 上传时间/更新时间
    publish_time: int = attrs.field(default = '', converter = convert_time, metadata={'source': 'publishDate'})

    # 上传时间/更新时间
    publish_date: str = attrs.field(default = '', metadata={'source': 'publishDate'})
    # 文件版本，用以区分披露文件的所属进程类型（申报稿、上会稿、注册稿或封卷稿）
    file_version: int = attr.field(default = None, metadata={'source': 'fileVersion'})

    # 文件所属进程类型，说明文件所属进度节点；由于科创板没有区分这两种类型，所以在科创板这里定义为一样的数据
    file_type_of_process: int = attrs.field(default = -1, metadata={'source': 'fileType'})
    
    # 文件所属审核类型，提交给权力机关的类型；由于科创板没有区分这两种类型，所以在科创板这里定义为一样的数据
    file_type_of_audit: int = attrs.field(default = -1, metadata={'source': 'fileType'})
    
    @property
    def file_type_of_process_desc(self):
        return SH_IPO_FileType_Enum(self.file_type_of_process).desc if self.file_type_of_process else ''

    @property
    def file_type_of_audit_desc(self):
        return SH_IPO_FileType_Enum(self.file_type_of_audit).desc if self.file_type_of_audit else ''


    # 归属项目id
    project_id: str = attrs.field(default = '', metadata={'source': 'stockAuditNum'})
    # 公司id
    company_id: str = attrs.field(default = '')
    # 公司名
    company_name: str = attrs.field(default = '', metadata={'source': 'companyFullName|stockAuditName'})
    
     # 文件所属阶段
    stage: str = attrs.field(default = '', metadata={'source': 'auditStatus'})

    @property
    def stage_name(self):
        return stage_name(self)
    
    pass

"""@Return 定义创业板公司其他披露消息数据
"""
@attrs.define
class SH_IPO_CompanyOtherItem(SH_IPO_CompanyProcessItem):
    @property
    def stage_name(self):
        return stage_name(self)
    
    @property
    def stage_status_name(self):
        return stage_status_name(self)

    pass


"""@Return 定义科创板公司原始数据,存储原始数据，用于后续解析及分析比对，存于mongodb，不搞关系型那套
而只有在文件、进程状态更新时，对其进行全部更新
"""
@attrs.define
class SH_IPO_CompanySourceItem(BaseItem):
    project_id: str = attrs.field(default = '', metadata={'source': 'projectId'})
    ipo_result: str = attrs.field(default = '', metadata={'source': 'ipoResult'})
    detail_result: str = attrs.field(default = '', metadata={'source': 'detailResult'})
    pass



def zrz_stage_status_convert(self, retrive_dict = {}): 
    result = None
    if self.stage == SH_ZRZ_STAGE.MUNICIPAL_PARTY_COMMITTEE.value :
        result = retrive_dict['commitiResult']
    if self.stage == SH_ZRZ_STAGE.REVIEW_COMMITTEE.value :
        result = retrive_dict['commitiResult']
    if self.stage == SH_ZRZ_STAGE.RESTRUCTURE_COMMITTEE.value :
        result = retrive_dict['commitiResult']
    if self.stage == SH_ZRZ_STAGE.RESTRUCTURE_COMMITTEE_OTHER.value :
        result = retrive_dict['commitiResult']
    
    if self.stage == SH_ZRZ_STAGE.REGIST_RESULT.value:
        result = retrive_dict['registeResult']
    if self.stage == SH_ZRZ_STAGE.SUSPEND.value:
        result = retrive_dict['suspendStatus']
    if result == '':
        return None
    return result


"""
再融资数据
"""
@attrs.define
class SH_ZRZ_Item(SH_IPO_Item):

    # 业务子类型
    biz_type: int = attrs.field(default = None, metadata={'source': 'bussinesType'}) 
    
    @property
    def biz_type_desc(self):
        return SH_ZRZ_BUSINESS_TYPE(self.biz_type).desc if self.biz_type else ''

    
    company_code : str = attrs.field(default = '', metadata={'source': 's_companyCode'}) # 公司证券代码
    stock_business_type: int = attrs.field(default = STOCK_BUSINESS_TYPE.ZRZ.value) # 所属业务
    stock_business_type_desc: str = attrs.field(default = STOCK_BUSINESS_TYPE.ZRZ.desc)

    def stage_status_convert(self, retrive_dict = {}): 
        return zrz_stage_status_convert(self, retrive_dict)
    
    def build_intermediary_convert(type):
        def intermediary_convert(list = []):
            intermediary_list = [item for i, item in enumerate(list) if item['i_intermediaryType'] == type]
            if len(intermediary_list) > 0:
                [intermediary, *other] = intermediary_list
                return intermediary
            else:
                return ''
        return intermediary_convert 


    @property
    def issue_market_desc(self):
        return SH_STOCK_TYPE(self.issue_market).desc if self.issue_market and SH_STOCK_TYPE(self.issue_market) else ''
    
    @property
    def stage_name(self):
        return stage_name(self, SH_ZRZ_STAGE)

    stage_status : int = attrs.field(default = None, metadata={'source': stage_status_convert}) # 阶段状态
    
    @property
    def stage_status_name(self):
        return stage_status_name(self, SH_ZRZ_STAGE)
        

    csrc_code : str = attrs.field(default = '') # 证监会分类代码
    csrc_desc : str = attrs.field(default = '') # 证监会分类代码说明

    # 律师事务所
    _law_office: dict = attrs.field(
        default={},
        metadata={'source': 'intermediary#{ "rule": "i_intermediaryType=%s"}'%(INTERMEDIARY_TYPE.LAW_FIRM.value)}
    )
    
    @property
    def law_office_id(self):
        return self._law_office['i_intermediaryId']
    
    @property
    def law_office_name(self):
        return self._law_office['i_intermediaryName']
    
    # 保荐机构，律师事务所，会计事务所，用了三种方式获取数据
    # 保荐机构
    _sponsor: dict = attrs.field(
        default={},
        converter=build_intermediary_convert(type = INTERMEDIARY_TYPE.SPONSOR.value),
        metadata={'source': 'intermediary'}
    )

    @property
    def sponsor_id(self):
        return self._sponsor['i_intermediaryId']
    
    @property
    def sponsor_name(self):
        return self._sponsor['i_intermediaryName']
    

    #sponsor_signatory_id : str = attrs.field(default = '')

    # 会计事务所
    accounting_firm_id : str = attrs.field(default = '',
        # 自定义格式
        metadata={'source': 'intermediary#{ "rule": "i_intermediaryType=%s", "path": "i_intermediaryId"}'%(INTERMEDIARY_TYPE.ACCOUNTING_FIRM.value)}
    )
    # 会计事务所
    accounting_firm_name : str = attrs.field(default = '',
        # 自定义格式
        metadata={'source': 'intermediary#{ "rule": "i_intermediaryType=%s", "path": "i_intermediaryName"}'%(INTERMEDIARY_TYPE.ACCOUNTING_FIRM.value)}
    )
    #accounting_firm_signatory_id : str = attrs.field(default = '')

    # 律师事务所
    _rating_agency: dict = attrs.field(
        default={},
        metadata={'source': 'intermediary#{ "rule": "i_intermediaryType=%s"}'%(INTERMEDIARY_TYPE.RATING_AGENCY.value)}
    )
    # 是否有更好的写法
    @property
    def rating_agency_id(self):
        return self._rating_agency['i_intermediaryId'] if 'i_intermediaryId' in self._rating_agency.keys() else ''
    
    @property
    def rating_agency_name(self):
        return self._rating_agency['i_intermediaryName'] if 'i_intermediaryName' in self._rating_agency.keys() else ''

    # 资产评估机构
    _asset_evaluation_institute: dict = attrs.field(
        default={},
        metadata={'source': 'intermediary#{ "rule": "i_intermediaryType=%s"}'%(INTERMEDIARY_TYPE.ASSET_EVALUATION_INSTITUTE.value)}
    )
    # 是否有更好的写法
    @property
    def asset_evaluation_institute_id(self):
        return self._asset_evaluation_institute['i_intermediaryId'] if 'i_intermediaryId' in self._asset_evaluation_institute.keys() else ''
    
    @property
    def asset_evaluation_institute_name(self):
        return self._asset_evaluation_institute['i_intermediaryName'] if 'i_intermediaryName' in self._asset_evaluation_institute.keys() else ''


    accept_apply_date : str = attrs.field(default = '', metadata={'source': 'auditApplyDate'}) #交易所受理时间
    accept_apply_time: int = attrs.field(default = None, converter = convert_time, metadata={'source': 'auditApplyDate'})
    
    update_date : str = attrs.field(default = '', metadata={'source': 'updateDate'}) #更新时间
    update_time: int = attrs.field(default = None, converter = convert_time, metadata={'source': 'updateDate'})

    create_date : str = attrs.field(default = '', metadata={'source': 'auditApplyDate'}) #公司发起申请时间
    create_time: int = attrs.field(default = None, converter = convert_time, metadata={'source': 'auditApplyDate'})
     # 人员信息存到另一个字段中
    # signing_attorney_id : str = attrs.field(default = '')
    pass