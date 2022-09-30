## KCB
### 字段说明

#### 项目状态类型
- status: 
  - 1：已受理
  - 2：已问询
  - 3： 上市委审议
    - 3-1 上市委会议通过
    - 3-2 有条件通过
    - 3-3 上市委会议未通过
    - 3-6 暂缓审议
  - 4 // 提交注册
  - 5 // 注册结果
    - 5-1: 注册生效
    - 5-2：不予注册
    - 5-3：终止注册
  - 6：已发行
  - 7： 中止财报及更新
    - 7-1 中止（财报更新）
    - 7-2 中止（其他事项）
  - 8：终止
  - 9: 复审委会议
    - 9-4 复审委会议通过
    - 9-5 复审委会议未通过
  - 10： 补充审核
  详见此代码：

```
    ysl: [{ cs: '1', rr: '', s: '已受理' }],
    ywx: [{ cs: '2', rr: '', s: '已问询' }],
    sswhyjg: [{ cs: '3,9', rr: '1,3,4,5,6', s: '上市委审议' }, { cs: '3', rr: '6', s: '暂缓审议' }, { cs: '3', rr: '1', s: '上市委会议通过' }, { cs: '3', rr: '3', s: '上市委会议未通过' }, { cs: '9', rr: '4', s: '复审委会议通过' }, { cs: '9', rr: '5', s: '复审委会议未通过' }],
    tjzc: [{ cs: '4', rr: '', s: '提交注册' }],
    bcsh: [{ cs: '10', rr: '', s: '补充审核' }],
    zcjg: [{ cs: '5', rr: '', s: '注册结果' }, { cs: '5', rr: '1', s: '注册生效' }, { cs: '5', rr: '2', s: '不予注册' }, { cs: '5', rr: '3', s: '终止注册' }],
    zzjcbgx: [{ cs: '7', rr: '', s: '中止及财报更新' }],
    zhz: [{ cs: '8', rr: '', s: '终止' }],
    
    
    if (status == "1") {
        return "已受理";
    } else if (status == "2") {
        return "已问询";
    } else if (status == "3") {
        if (subStatus == "1") {
            return "上市委会议通过";
        } else if (subStatus == "2") {
            return "有条件通过";
        } else if (subStatus == "3") {
            return "上市委会议未通过";
        } else if (subStatus == "6") {
            return "暂缓审议";
        }
        return "上市委会议";
    } else if (status == "4") {
        return "提交注册";
    } else if (status == "5") {
        if (registeResult == "1") {
            return "注册生效";
        } else if (registeResult == "2") {
            return "不予注册";
        } else if (registeResult == "3") {
            return "终止注册";
        }
        return "注册结果";
    } else if (status == "6") {
        return "已发行";
    } else if (status == "7") {
        var suspendStatus = data.suspendStatus || '';
        if (suspendStatus == "1") {
            return "中止（财报更新）"
        } else if (suspendStatus == "2") {
            return "中止（其他事项）"
        } else {
            return "中止及财报更新";
        }
    } else if (status == "8") {
        return "终止";
    } else if (status == "9") {
        if (subStatus == "4") {
            return "复审委会议通过";
        } else if (subStatus == "5") {
            return "复审委会议未通过";
        }
        return "复审委会议";
    } else if (status == "10") {
        return "补充审核";
    } else { return "-"; }
```


#### GS 表
- OPERATION_SEQ: 操作流水号，理解为操作唯一标识符
- auditApplyDate: 申请时间 //"20210512160054"
- collectType: 1 // 申请类型
- commitiResult: "" // 委员会审议结果（上市委 及 复审委）
- createTime: // 创建时间  "20210425163737" 
- currStatus: 5 // 当前状态
- intermediary: // 中间人(1-承销商、2-会计事务所、3-律所、4-资产评估事务所) ，其中，类型4非必须
- issueAmount: "" // 募资期数？ 但貌似没有用到
- issueMarketType: // 市场类型
- planIssueCapital: 15.0208 // 拟募资总额
- registeResult: 1 // 注册结果（如currStatus有子状态，则与其拼接得到最终状态）
- stockAuditName: // 申请名称
- stockAuditNum: "874" // 申请序号
- stockIssuer: // 高管 An issuer is a legal entity that develops, registers and sells securities to finance its operations.
- suspendStatus: "" // 项目暂缓状态
- updateDate: "20220215101346" // 最新更新时间
- wenHao: "" // 未找到使用说明

#### 中间人表（Intermediary Table）
- auditId: 审核序号，与GS表中的stockAuditNum对应
- i_intermediaryAbbrName: // 中间人简称
- i_intermediaryId: // 中间人ID
- i_intermediaryName: // 中间人全称
- i_intermediaryOrder: // 中间人排序
- i_intermediaryType: // 中间人类型

#### 中间人参与人表（Intermediary_Person Table）
- i_p_jobTitle: // 职位抬头
- i_p_jobType: 21 // 职位类型
- i_p_personId: // 人员ID
- i_p_personName: "徐浙鸿" // 姓名

> PS: 不确定是否为独立表

> PS2: 
> type=1有：保荐业务负责人、保荐代表人A、保荐代表人B、项目协办人
> type=2有：会计事务所负责人、签字会计师A、签字会计师B
> type=3有：律师事务所负责人、签字律师A、签字律师B、签字律师C（或有）
> type=4有：评估事务所负责人、签字评估师A、签字评估师B（如有）

#### 公司高管表
- auditId: "874" // 审核序号，与GS表中的stockAuditNum对应
- s_areaNameDesc: // 审核地区（市）
- s_companyCode: "" // 公司Code，不知道对应的是哪个Code，未上市应该没有code，除非是工商局
- s_csrcCode: "C39" // 行业代码
- s_csrcCodeDesc:  // 行业代码简介
- s_issueCompanyAbbrName: // 公司简称
- s_issueCompanyFullName: // 公司全称
- s_jobTitle: // 职位抬头
- s_personId: // 人员Id
- s_personName: "冯志峰" // 姓名
- s_province: "广东" // 公司所在省
- s_stockIssueId: "874" // ZS市场Id，与审核序号相同

### API请求
#### 拉取数据结果
- http://query.sse.com.cn/statusAction.do?jsonCallBack=jsonpCallback4695&offerType=&commitiResult=&registeResult=&csrcCode=&currStatus=5&province=&order=updateDate%7Cdesc&keyword=&auditApplyDateBegin=&auditApplyDateEnd=&isPagination=true&sqlId=SH_XM_LB&pageHelp.pageSize=20&pageHelp.pageNo=2&pageHelp.beginPage=2&pageHelp.endPage=2&_=1646036319016
	- 这里要注意：
	  - 要获取上市委和复审委会议结果时，要传递：
	    - currStatus = '3,9';  commitiResult = '1,3,4,5,6';

	    
	    
### 其他
#### KCB SQL表
- GP_GPZCZ_XMDTDLLB

```
  /* 科创板股票审核下拉框数据渲染 */
function getselect() {
    var _this = this
    optionParams = {
      'sqlId':'GP_GPZCZ_XMDTDLLB',
      'isPagination':false
    }
```


## CYB

### 字段说明

#### 项目状态
displayStatusName: null // 展示状态名
id: null
projectCount: 9 // 状态总量
projectStatusList: [
// 子状态列表
{
displayStatusName: null
id: null
projectCount: 9
projectStatusList: []
remark: null
stage: 10 // 状态stage值
stageName: "受理" // 状态stage名
status: 20 // 状态值
statusName: "新受理" // 状态名
statusSortNo: null
}]
remark: null
stage: 10
stageName: "受理"
status: null
statusName: null
statusSortNo: null


- 10 // 受理
	- status: 20 // 新受理
- 20 // 问询
	- status: 30 // 已问询
- 30 // 上市委会议
	- status: 45 // 上市委会议通过
	- status: 44 // 上市委会议未通过
	- status: 46 // 暂缓审议
	- status: 56 // 上市委复审会议通过
	- status: 54 // 上市委复审会议通过
- 35 // 提交注册
	- status: 60 // 提交注册
- 40
	- status: 70 // 注册生效
	- status: 74 // 不予注册
	- status: 76 // 补充审核
	- status: 78 // 终止注册
- 50 // 中止
	- status: 80 // 中止
- 60 // 终止
	- status: 90 // 终止(审核不通过)
	- status: 95 // 终止(撤回)
	- status: 94 // 终止（未在规定时限内回复）

#### GS 表
acctfm: "容诚会计师事务所（特殊普通合伙）" // 会计事务所全称
- acctsgnt: null
- acptdt: "2022-01-28"// 交易所接受时间
approveProcessType: null
approveProcessTypeName: ""
biztyp: null
biztype: 1 // 项目业务类型
biztypsb: null
biztypsbName: ""
cmpcode: ""
cmpnm: "" // 公司名称
cmpsnm: "" // 公司简称
csrcind: ""  // 所属行业名称
drafIpoCorp: null // 
entid: null
evalinst: null
evalsgnt: null
hasDraftIpoCorp: null
isCashPurchase: null
isCsrcPrepared: null
isRaiseComplementFinance: null
issueTargetName: ""
issueTargetType: null
jsprcd: null
jsprinst: null
jsprinsts: ""
jsprrep: null
lastestAuditEndDate: null
lawfm: "上海市锦天城律师事务所" 
lglsgnt: null
maramt: "4.63" // 拟募资金额（亿元）
pjdot: null
pjreson: null
planIssuseCapitalForFinancing: null // 融资金额
planIssuseCapitalForPurchase: null // 收购金额
plnmt: null
prjid: 1001997 // 项目id
prjprog: null // 项目进度，不知道是什么单位
prjst: "已问询" // 项目状态展示名称
prjstatus: 30 // 项目状态，与👆的项目状态的子状态列表中的status保持一致
regloc: "安徽" // 所属省
sprcd: "000680" // 承销商代码
sprinst: "中信建投证券股份有限公司" // 承销商全称
sprinsts: "中信建投" // 承销商简称
sprrep: null // 承销商位置
stage: 20 // 当前位置，父状态
sts: null
updtdt: "2022-03-02" // 更新时间
