from enum import Enum
from typing import Any, Callable

from crawler.util.decorator import wrap_extend_enum

"""
枚举均按此格式： name = (value, desc)
"""

"""基础枚举类
"""
class BaseEnum(Enum):
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Enum):
            return self.value == other.value
    def __new__(cls, value, desc):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.desc = desc
        return obj
        # return super(BaseEnum, metacls).__new__(metacls, cls, value, desc) 

extend_enum = wrap_extend_enum(BaseEnum)
class DictEnum(Enum):
    def __new__(cls, dict):
        obj = object.__new__(cls)
        for key, value in dict.items():
            if key == 'value':
                obj._value_ = value
            else:
                setattr(obj, key, value)
        return obj

"""
证券交易所的上市业务
"""
class STOCK_BUSINESS_TYPE(BaseEnum):
    IPO = (1, 'IPO')
    ZRZ = (2, '再融资')
    ZCCZ = (3, '重大资产重组')
    ZBSS = (4, '转板上市')

"""
上海证券交易所上市板块
"""
class SH_STOCK_TYPE(BaseEnum):
    KCB = (1, '科创板')
    ZB = (2, '沪市主板')



"""
上市交易所
"""
class STOCK_EXCHANGE_TYPE(BaseEnum):
    KCB = (1, '科创板')
    CYB = (2, '创业板')
    SH_ZB = (3, '沪市主板')
    SZ_ZB = (4, '深市主板')
    XSB = (5, '新三板')
    # HK_STOCK = (6, '香港股票')
    # US_STOCK = (7, '美国股票')
    # CN_STOCK = (8, '中国股票')
    # SH_STOCK = (9, '上海股票')
    # SZ_STOCK = (10, '深圳股票')
    # SH_INDEX = (11, '上海指数')
    # SZ_INDEX = (12, '深圳指数')
    # HK_INDEX = (13, '香港指数')
    # US_INDEX = (14, '美国指数')
    # CN_INDEX = (15, '中国指数')
    # SH_FUND = (16, '上海基金')
    # SZ_FUND = (17, '深圳基金')
    # HK_FUND = (18, '香港基金')
    # US_FUND = (19, '美国基金')
    # CN_FUND = (20, '中国基金')
    # SH_BOND = (21, '上海债券')
    # SZ_BOND = (22, '深圳债券')
    # HK_BOND = (23, '香港债券')
    # US_BOND = (24, '美国债券')
    # CN_BOND = (25, '中国')

"""@Return 交易所业务中介机构类型(交易所视角公司类型)
"""
class INTERMEDIARY_TYPE(BaseEnum):
     # 一般企业
    NORMAL = (-999, '一般企业')

    # 保荐机构
    SPONSOR = (1, '保荐机构')

    # 律师事务所
    LAW_FIRM = (3, '律师事务所')

    # 会计事务所
    ACCOUNTING_FIRM = (2, '会计事务所')

    # 资产评估机构
    ASSET_EVALUATION_INSTITUTE = (4, '资产评估机构')

    # 资信评级机构
    RATING_AGENCY = (5, '资信评级机构')

"""@deprected
@Return 交易所视角公司类型
"""
# @extend(INTERMEDIARY_TYPE)
class COMPANY_TYPE(BaseEnum):
    # 一般企业
    NORMAL = (0, '一般企业')

    # 保荐机构
    SPONSOR = (1, '保荐机构')

    # 律师事务所
    LAW_FIRM = (2, '律师事务所')

    # 会计事务所
    ACCOUNTING_FIRM = (2, '会计事务所')

    # 资产评估机构
    ASSET_EVALUATION_INSTITUTE = (4, '资产评估机构')

    # 资信评级机构
    RATING_AGENCY = (5, '资信评级机构')
    


"""@Return 上海交易所IPO各阶段
"""
class SH_IPO_STAGE(DictEnum):
    # 受理阶段
    ACCEPT = ({
        "value":1, 
        "desc": '受理阶段',
        "status": []
    })

    # 问询回复
    INQUERY = ({
        "value": 2, 
        "desc": '问询回复',
        "status": []
    })

    # 上市委会议
    MUNICIPAL_PARTY_COMMITTEE = ({
        "value": 3, 
        "desc": '上市委会议',
        "status": [
            {
                "name": '上市委会议通过',
                "value": 1,
            },
            {
                "name": '有条件通过',
                "value": 2,
            },
            {
                "name": '上市委未通过',
                "value": 3,
            },
            {
                "name": '上市委暂缓审议',
                "value": 6,
            }
        ]
    })

    # 提交注册
    APPLY_REGIST = ({
        "value": 4, 
        "desc": '提交注册',
        "status": []
    })

    # 注册结果
    REGIST_RESULT = ({
        "value": 5, 
        "desc": '注册结果',
        "status": [
            {
                "name": '注册生效',
                "value": 1,
            },
            {
                "name": '不予注册',
                "value": 2,
            },
            {
                "name": '终止注册',
                "value": 3,
            }
        ]
    })

    # 已发行
    ISSUED = ({
        "value": 6, 
        "desc": '已发行',
        "status": []
    })

    # 中止
    SUSPEND = ({
        "value": 7, 
        "desc": '中止',
        "status": [
            {
                "name": '中止，财报更新',
                "value": 1,
            },
            {
                "name": '中止，其他事项',
                "value": 2,
            }
        ]
    })

    # 终止
    END = ({
        "value": 8, 
        "desc": '终止',
        "status": []
    })
    
    # 复审委会议
    REVIEW_COMMITTEE = ({
        "value": 9, 
        "desc": '复审委会议',
        "status": [
            {
                "name": '复审委通过',
                "value": 1,
            },
            {
                "name": '复审委不通过',
                "value": 2,
            }
        ]
    })

    # 补充审核
    SUPPLEMENTARY_AUDIT = ({
        "value": 10, 
        "desc": '补充审核',
        "status": []
    })



class STAGE_STATUS(BaseEnum):
    UNKNOWN = (-999, '未知')
    DONE = (999, '成功')
    


"""@Return 上海交易所IPO文件类型
"""
class SH_IPO_FileType_Enum(BaseEnum):
    
    CONSIDERATION_OF_THE_MEETING = (1, '审议会议公告')

    RESULT_CONSIDERATION_OF_THE_MEETING = (2, '审议会议结果公告')
    
    INQUERY = (5, '问询')

    REPLY = (6, '回复')

    ZHU_GU_SHUO_SHU = (30, '招股说明书')
    # 发行保荐书
    FA_XING_BAO_JIANG_SHU = (36, '发行保荐书')
    # 上市保荐书
    SHANG_SHI_BAO_JIANG_SHU = (37, '上市保荐书')
    # 审计报告
    SHEN_JI_BAO_GAO = (32, '审计报告')
    # 法律意见书
    FA_LU_YI_JIAN_SHU = (33, '法律意见书')
    # 其他
    MU_JI_SHUO_SHU = (34, '其他')
    # 注册结果通知
    REGIST_RESULT = (35, '注册结果通知')
    # 终止
    END = (38, '终止')


"""
上证所再融资stage状态
"""
class SH_ZRZ_STAGE(DictEnum):
    # 受理阶段
    ACCEPT = ({
        "value":1, 
        "desc": '已受理',
        "status": []
    })

    # 问询
    INQUERY = ({
        "value": 2, 
        "desc": '已问询',
        "status": []
    })

    # 回复
    REPLY = ({
        "value": 3, 
        "desc": '已回复',
        "status": []
    })

    APPLY = ({
        "value": 4, 
        "desc": '通过',
        "status": []
    })

    DELAY = ({
        "value": 5, 
        "desc": '暂缓审议',
        "status": []
    })

    REJECT = ({
        "value": 6, 
        "desc": '未通过',
        "status": []
    })

    # 复审委会议
    REVIEW_COMMITTEE = ({
        "value": 40, 
        "desc": '复审委会议',
        "status": [
            {
                "name": '复审委通过',
                "value": 4,
            },
            {
                "name": '复审委不通过',
                "value": 5,
            }
        ]
    })

    # 重组联席会议
    RESTRUCTURE_COMMITTEE = ({
        "value": 25, 
        "desc": '重组联席会议',
        "status": [
            {
                "name": '重组联席会议通过',
                "value": 1,
            },
            {
                "name": '重组联席会议不通过',
                "value": 3,
            }
        ]
    })

    # 重组联席会议，另一个字段
    RESTRUCTURE_COMMITTEE_OTHER = ({
        "value": 30, 
        "desc": '重组联席会议',
        "status": [
            {
                "name": '重组联席会议通过',
                "value": 1,
            },
            {
                "name": '重组联席会议不通过',
                "value": 3,
            }
        ]
    })

    # 上市委会议
    MUNICIPAL_PARTY_COMMITTEE = ({
        "value": 35, 
        "desc": '上市委会议',
        "status": [
            {
                "name": '上市委会议通过',
                "value": 1,
            },
            {
                "name": '上市委未通过',
                "value": 3,
            }
        ]
    })

    # 提交注册
    APPLY_REGIST = ({
        "value": 45, 
        "desc": '提交注册',
        "status": []
    })


    SUPPLEMENTARY_AUDIT_INQUERY = ({
        "value": 46, 
        "desc": '补充审核已问询',
        "status": []
    })

    SUPPLEMENTARY_AUDIT_REPLY = ({
        "value": 47, 
        "desc": '补充审核已回复',
        "status": []
    })

    # 注册结果
    REGIST_RESULT = ({
        "value": 50, 
        "desc": '注册结果',
        "status": [
            {
                "name": '注册生效',
                "value": 1,
            },
            {
                "name": '不予注册',
                "value": 2,
            },
            {
                "name": '终止注册',
                "value": 3,
            }
        ]
    })

    # 中止
    SUSPEND = ({
        "value": 55, 
        "desc": '中止',
        "status": [
            {
                "name": '中止，财报更新',
                "value": 1,
            },
            {
                "name": '中止，其他事项',
                "value": 2,
            }
        ]
    })

    # 终止
    END = ({
        "value": 60, 
        "desc": '终止',
        "status": []
    })



"""@Return 上海交易所IPO文件类型
"""
class SH_ZRZ_FILE_TYPE(BaseEnum):
    
    INQUERY = (11, '问询')

    REPLY = (12, '回复')    

    ZHU_GU_SHUO_SHU = (30, '募集说明书')
    # 发行保荐书
    FA_XING_BAO_JIANG_SHU = (31, '发行保荐书')
    
    # 审计报告
    SHEN_JI_BAO_GAO = (32, '审计报告')
    # 法律意见书
    FA_LU_YI_JIAN_SHU = (33, '法律意见书')
    # 其他
    MU_JI_SHUO_SHU = (34, '其他')
    
    ZHU_GU_SHUO_SHU_GAI_LANG = (35, '募集说明书概览')

    # 上市保荐书
    SHANG_SHI_BAO_JIANG_SHU = (53, '上市保荐书')

    ZHENG_JIAN_HUI_JUE_DING = (46, '注册结果通知')

    ZHONG_ZHI_SHEN_HE_JUE_DING = (45, '终止审核决定')

    # 其实51与52都是 上市委会议公告与结果 ，只不过枚举值需要进行区分
    SHANG_SHI_WEI_HUI_YI_JIE_GUO = (51, '上市委会议公告与结果')

    SHANG_SHI_WEI_HUI_YI_GONG_GAO = (52, '上市委会议公告与结果')



"""
上证所业务类型枚举
业务类型(businessType)再融资方式
	1
		公开增发股票
	2
		配股
	3
		非公开发行股票
	4
		公开发行存托凭证
	5
		非公开发行存托凭证
	6
		公开发行可转债
	7
		定向可转债
	8
		优先股
	9
		非公开发行股票（简易程序）
	10
		定向可转债（简易程序）
"""
class SH_ZRZ_BUSINESS_TYPE(BaseEnum):
    GKZFGP = (1, '公开增发股票')
    PG = (2, '配股')
    FGKZFGP = (3, '非公开发行股票')
    
    GKFXCTPZ = (4, '公开发行存托凭证')
    FGKFXCTPZ = (5, '非公开发行存托凭证')
    
    GKFXCKZZ = (6, '公开发行可转债')
    DXKZZ = (7, '定向可转债')

    YXG = (8, '优先股')

    FGKFXGP_JY = (9, '非公开发行股票（简易程序）')
    DXKZZ_JY = (10, '定向可转债（简易程序）')


# 创业板各阶段
# class SZ_IPO_STAGE(BaseEnum):
#     # 受理阶段
#     ACCEPT = (10, '受理阶段')
#     # ACCEPT = ({'value': 10, 'desc': '受理阶段', 'status': []})

#     # 问询回复
#     INQUERY = (20, '问询回复')

#     # 上市委会议
#     MUNICIPAL_PARTY_COMMITTEE = (30, '上市委会议')

#     # 提交注册
#     APPLY_REGIST = (35, '提交注册')

#     # 注册结果
#     REGIST_RESULT = (40, '注册结果')

#     # 中止
#     SUSPEND = (50, '中止')

#     # 终止
#     END = (60, '终止')


"""
深圳证券交易所上市板块
"""
class SZ_STOCK_TYPE(BaseEnum):
    CYB = (16, '创业板')
    ZB = (12, '深市主板')

class SZ_IPO_STAGE(DictEnum):
    # 受理阶段
    # ACCEPT = (10)
    ACCEPT = (
        {'value': 10, 'desc': '受理阶段', 'status': [
            {
                "name": '新受理',
                "value": 20,
            }
        ]}
    )

    # 问询回复
    INQUERY = ({
        'value': 20,
        'desc': '问询回复',
        "status": [
            {
                "name": '已问询',
                "value": 30,
            }
        ]
    })

    # 上市委会议
    MUNICIPAL_PARTY_COMMITTEE = ({
        'value': 30,
        'desc': '上市委会议',
        "status": [
            {
                "name": '上市委会议',
                "value": 40,
            },
            {
                "name": '上市委会议未通过',
                "value":44,
            },
            {
                "name": '上市委会议未通过',
                "value": 47,
            },
            {
                "name": '上市委会议通过',
                "value": 45,
            },
            {
                "name": '上市委会议通过',
                "value": 48,
            },
            {
                "name": '暂缓审议',
                "value": 46,
            },
            {
                "name": '上市委复审会议未通过',
                "value": 54,
            },
            {
                "name": '上市委复审会议未通过',
                "value":55,
            },
             {
                "name": '上市委复审会议通过',
                "value": 56,
            },
            {
                "name": '上市委复审会议通过',
                "value": 57,
            }
        ]
    })

    # 提交注册
    APPLY_REGIST = ({
        'value': 35,
        'desc': '提交注册',
        "status": [
            {
                "name": '提交注册',
                "value": 60,
            }
        ]
    })

    # 注册结果
    REGIST_RESULT = ({
        'value': 40,
        'desc': '注册结果',
        "status": [
            {
                "name": '注册生效',
                "value": 70,
            },
            {
                "name": '不予注册',
                "value": 74,
            },
            {
                "name": '补充审核',
                "value": 76,
            },
            {
                "name": '终止注册',
                "value": 78,
            }
        ]
    })

    # 中止
    SUSPEND = ({
        'value': 50,
        'desc': '中止',
        "status": [
            {
                "name": '中止',
                "value": 80,
            }
        ]
    })

    # 终止
    END = ({
        'value': 60,
        'desc': '终止',
        "status": [
            {
                "name": '终止（审核不通过）',
                "value": 90,
            },
            {
                "name": '终止（未在规定时限内回复）',
                "value": 94,
            },
            {
                "name": '终止（撤回）',
                "value": 95,
            }
        ]
    })


# 创业板文件进程类型
class SZ_IPO_FileTypeOfProcessEnum(BaseEnum):
    # 申报稿
    APPLY = (1, '申报稿')

    # 上会稿
    MUNICIPAL_PARTY_COMMITTEE = (2, '上会稿')

    # 注册稿
    APPLY_REGIST = (3, '注册稿')

    # 回复意见
    REPLY = (4, '回复意见')

    # 审议公告
    REVIEW_NOTICE = (5, '审议公告')
    
    # 上市委结果公告
    MUNICIPAL_PARTY_COMMITTEE_RESULT = (6, '上市委结果公告')

    # 证监会结果批复
    REGIST_RESULT = (7, '证监会结果批复')

     # 终止
    END = (10, '终止')

    # 补充审议公告
    SUPPLEMENT_REVIEW_NOTICE = (18, '补充审议公告')

    # 更新问询回复文件
    UPDATE_INQUERY = (20, '更新问询回复文件')

    # 问询函
    INQUERY = (22, '问询函')

class SZ_IPO_FileTypeOfAuditEnum(BaseEnum):
    # 招股说明书
    # 枚举按此格式： name = (value, desc)
    ZHU_GU_SHUO_SHU = (3, '招股说明书')
    # 发行保荐书
    FA_XING_BAO_JIANG_SHU = (4, '发行保荐书')
    # 上市保荐书
    SHANG_SHI_BAO_JIANG_SHU = (5, '上市保荐书')
    # 审计报告
    SHEN_JI_BAO_GAO = (6, '审计报告')
    # 法律意见书
    FA_LU_YI_JIAN_SHU = (7, '法律意见书')
    # 募集说明书
    MU_JI_SHUO_SHU = (9, '募集说明书')
    # 估值报告
    GU_ZHI_BAO_GAO = (11, '估值报告')
    # 重大资产重组报告书
    CHONG_DA_ZI_CHANG_ZU_BAO_GAO = (12, '重大资产重组报告书')


# 创业板文件进程类型到stage的映射
SZ_IPO_FileTypeOfProcess_TO_SZ_IPO_STAGE = {
    SZ_IPO_FileTypeOfProcessEnum.APPLY.value: SZ_IPO_STAGE.ACCEPT.value,
    SZ_IPO_FileTypeOfProcessEnum.MUNICIPAL_PARTY_COMMITTEE.value: SZ_IPO_STAGE.MUNICIPAL_PARTY_COMMITTEE.value,
    SZ_IPO_FileTypeOfProcessEnum.APPLY_REGIST.value: SZ_IPO_STAGE.APPLY_REGIST.value,
    SZ_IPO_FileTypeOfProcessEnum.REPLY.value: SZ_IPO_STAGE.INQUERY.value,
    SZ_IPO_FileTypeOfProcessEnum.REVIEW_NOTICE.value: SZ_IPO_STAGE.MUNICIPAL_PARTY_COMMITTEE.value,
    SZ_IPO_FileTypeOfProcessEnum.MUNICIPAL_PARTY_COMMITTEE_RESULT.value: SZ_IPO_STAGE.MUNICIPAL_PARTY_COMMITTEE.value,
    SZ_IPO_FileTypeOfProcessEnum.REGIST_RESULT.value: SZ_IPO_STAGE.REGIST_RESULT.value,
    SZ_IPO_FileTypeOfProcessEnum.END.value: SZ_IPO_STAGE.END.value,
    SZ_IPO_FileTypeOfProcessEnum.SUPPLEMENT_REVIEW_NOTICE.value: SZ_IPO_STAGE.MUNICIPAL_PARTY_COMMITTEE.value,
    SZ_IPO_FileTypeOfProcessEnum.SUPPLEMENT_REVIEW_NOTICE.value: SZ_IPO_STAGE.MUNICIPAL_PARTY_COMMITTEE.value,
    SZ_IPO_FileTypeOfProcessEnum.UPDATE_INQUERY.value: SZ_IPO_STAGE.INQUERY.value,
    SZ_IPO_FileTypeOfProcessEnum.INQUERY.value: SZ_IPO_STAGE.INQUERY.value,
}


# 主板IPO状态
class ZB_STAGE(BaseEnum):
    PRE_REVEAL = (1, '预披露')
    PRE_REVEAL_UPDATE = (2, '预披露更新')

@extend_enum(ZB_STAGE)
class ZB_FILE_TYPE_OF_PROCESS(BaseEnum):
    pass

class ZB_FILE_TYPE_OF_AUDIT(BaseEnum):
    # 招股说明书
    ZHU_GU_SHUO_SHU = (3, '招股说明书')