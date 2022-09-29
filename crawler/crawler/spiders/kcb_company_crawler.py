# -*- coding: utf-8 -*-

import scrapy
import urllib
import time
import datetime
import json
import copy
import os
from pydash import objects

from crawler.items.base import MarketCountItem
from crawler.items.kcb import CompanyItem, IPOItem, CompanyManagerItem, IntermediaryItem, KCBIntermediaryItem, KCBIntermediaryPersonItem,KCBCompanyMilestoneItem, KCBCompanyProcessItem,KCBFileItem, KCBCompanyOtherItem
from crawler.util.constant import COMPANY_TYPE,KCB_STAGE, STOCK_EXCHANGE_TYPE
from crawler.util import util
from crawler.util import decorator
from crawler.util import jsonp # 对应模块 ../util/jsonp.py, 模块加载是以脚本所在目录结构为根目录
from crawler.util.postgre import KCBPostgreConnector

# from crawler.items import CrawlerItem

# =============================================================================
# 获取科创板当前过会进程中的公司
# 增量更新两个办法：1.是走sql，先find后插入；2.走redis，使用数据指纹（id+updateTime+stage+stage_status）走增量开发。
# =============================================================================
class KCBCompanySpider(scrapy.Spider):
    name = "kcb_company"
    
    custom_settings = {'ITEM_PIPELINES': {'crawler.pipelines.KCBPipeline': 300}}

    params = {
        # "jsonCallBack": 'jsonCallback' + str(round(time.time() * 1000)),
        "isPagination": True,
        "sqlId": 'SH_XM_LB',
        "pageHelp.pageSize": 100,
        # "pageHelp.pageNo": 1,
        "_": round(time.time() * 1000),
        "offerType": '',
        "commitiResult": '',
        "registeResult": '',
        "csrcCode": '',
        "currStatus": '',
        "province": '',
        "order": 'updateDate|desc',
        "keyword": '',
        "auditApplyDateBegin": '',
        "auditApplyDateEnd": '',
    }
    
    is_yield = True
    
    download_all = False

    pageCount = 0    
    
    totalCount = 0
    
    start_time = 0
    
    start_time_str = ''
    
    headers = {
        "Referer": "http://star.sse.com.cn/"
    }
    
    cookies = {
        "yfx_c_g_u_id_10000042": "ck22022520090216302302193303981",
        "yfx_f_l_v_t_10000042": "f_t_1645790942421__r_t_1645790942421__v_t_1645790942421__r_c_0"
    }
    
    target_url = 'http://query.sse.com.cn/statusAction.do'

    detail_headers = {
        "Referer": "http://kcb.sse.com.cn/"
    }
    detail_cookies = {
        'yfx_c_g_u_id_10000042': '_ck21022121261410069772517758114',
         'yfx_f_l_v_t_10000042': 'f_t_1613913973987__r_t_1657514138370__v_t_1657514138370__r_c_9'
    }

    detail_url = 'http://query.sse.com.cn/commonSoaQuery.do'

    detail_params = [
        {
            'type': 'detail',
            #'jsonCallBack': 'jsonpCallback17952076'
            'sqlId': 'SH_XM_LB'
            #stockAuditNum: 1045
            #_: 1657514175909
        },
        {
            'type': 'milestone',
            #jsonCallBack: jsonpCallback54987988
            'sqlId': 'GP_GPZCZ_XMDTZTTLB'
        },
        {
            'type': 'progress',
            'sqlId': 'GP_GPZCZ_XMDTZTYYLB',
            'order': 'qianDate|desc'

        },
        {
            'type': 'files',
            'sqlId': 'GP_GPZCZ_SHXXPL'
        },
        {
            'type': 'csrc_files',
            'sqlId': 'GP_GPZCZ_SSWHYGGJG',
            'fileType': '1,2,3,4'
        }
    ]
    
    company = []
    company_items = {}
    
    company_detail = []
    company_detail_items = {}
    
    ipo_map = {}

    ipo_obj = {
        "company": {},
        "ipo": {},
        "milestones": [],
        "process": [],
        "others": [],
        "files": [],

    }

    @decorator.inject_config   
    def __init__(self):
        self.connector = KCBPostgreConnector()

    # @classmethod
    # def from_crawler(cls, crawler):
    #     return cls(crawler.stats)
    
    def get_current_time(self): 
        current_milli_time = lambda: int(round(time.time() * 1000))
        return current_milli_time()
    
    def get_time_str(self, milli_time):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(milli_time/1000)) 
    
    def prepare_params(self, pageNo):
        request_params = copy.deepcopy(self.params)
        
        # 补充参数
        request_params['jsonCallBack'] = 'jsonCallback' + str(round(time.time() * 1000))
        
        request_params['pageHelp.pageNo'] = pageNo
        
        return '?' + urllib.parse.urlencode(request_params)

    def preapre_detail_params(self, detail_param, project_id):
        params = copy.deepcopy(detail_param)
        params['stockAuditNum'] = project_id
        params['jsonCallBack'] = 'jsonCallback' + str(round(time.time() * 1000))
        params['_'] = self.get_current_time()
        params['isPagination'] = False
        
        return '?' + urllib.parse.urlencode(params)

    def start_requests(self):
        urls = [
            self.target_url
        ]
        
        self.start_time = self.get_current_time()
        self.start_time_str = self.get_time_str(self.start_time)
        
        for url in urls:
            url = url + self.prepare_params(pageNo = 1)
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, cookies=self.cookies)
    
    def appendCralwInfo(self, companyInfo, url):
        companyInfo['crawlSource'] = url
        
        current_milli_time = lambda: int(round(time.time() * 1000))
        companyInfo['crawlTime'] = current_milli_time()
        companyInfo['crawlTimeString'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(current_milli_time()/1000)) 
        print(companyInfo)
        return companyInfo
     
    def parse(self, response): 
 
        json_dict = jsonp.loads_jsonp(_jsonp=response.text)
        
        
        # 获取结果
        result = json_dict['result']
        # 获取页码
        pageSetting = json_dict['pageHelp']
        
        # 获取所有页数
        self.pageCount = pageSetting['pageCount']
        
        # self.totalCount = pageSetting['total']
        
        currentPageNo = pageSetting['pageNo']
        
        if self.totalCount == 0:
            self.totalCount = pageSetting['total']
            count_item = MarketCountItem()
            count_info = {
                'count': self.totalCount,
                'stock_exchange_type': STOCK_EXCHANGE_TYPE.KCB.value
            }
            
            count_item.load_item(retrive_dict = count_info)
            yield count_item
        #origin = json_dict['origin']
        #print("公网ip: ",response.headers)
        
        for companyInfo in result:
            # 添加公司信息
            company_item = CompanyItem()
            company_item.load_item(retrive_dict = companyInfo)
            company_item.csrc_company_type = COMPANY_TYPE.NORMAL.value
            
            ipo_item = IPOItem()
            ipo_item.load_item(retrive_dict = companyInfo)
            ipo_item.company_id = company_item.id

            trigger_item_pipeline = False
            
            is_ipo_existed = self.connector.is_ipo_existed(project_id=ipo_item.project_id)
            trigger_item_pipeline = not is_ipo_existed
            is_ipo_updated = None
            if is_ipo_existed:
                is_ipo_updated = self.connector.is_ipo_updated(project_id=ipo_item.project_id, update_time=ipo_item.update_time, update_date=ipo_item.update_date)
                trigger_item_pipeline = is_ipo_updated
                print(f'is_ipo_existed:{is_ipo_existed}, is_ipo_updated:{is_ipo_updated}')
            else: 
                yield company_item
            
            
            # 写文件数据准备
            if ipo_item.project_id not in self.ipo_map.keys():                
                ipo_obj = copy.deepcopy(self.ipo_obj)
                ipo_obj['ipo'] = ipo_item.to_dict()
                ipo_obj['company'] = company_item.to_dict()
                self.ipo_map[ipo_item.project_id] = ipo_obj

            
            if trigger_item_pipeline or self.download_all:
                
                print(ipo_item.to_dict())
                yield ipo_item
                

                # 写文件数据准备            
                ipo_obj = copy.deepcopy(self.ipo_obj)
                ipo_obj['ipo'] = ipo_item.to_dict()
                ipo_obj['company'] = company_item.to_dict()
                
                # 公司高管信息
                company_managers = companyInfo['stockIssuer']
                for manager in company_managers:
                    manager_item = CompanyManagerItem()
                    manager_item.load_item(retrive_dict = manager)
                    manager_item.company_id = company_item.id
                    yield manager_item
                    #print(manager_item.to_dict())

                # 中介信息,循环生成
                intermediarys = companyInfo['intermediary']
                for intermediary in intermediarys:

                    intermediary_item = IntermediaryItem()
                    intermediary_item.load_item(retrive_dict = intermediary)
                    yield intermediary_item
                    intermediary_kcb_item = KCBIntermediaryItem()
                    intermediary_kcb_item.load_item(retrive_dict = intermediary)
                    yield intermediary_kcb_item
                    
                    intermediary_persons = intermediary['i_person']
                    # 中介人员信息，循环生成
                    for intermediary_person in intermediary_persons:
                        person_item = KCBIntermediaryPersonItem()
                        person_item.load_item(retrive_dict = objects.assign({}, intermediary_person, intermediary))
                        yield person_item
                # 查询详情数据
                for param in self.detail_params:
                    detail_params = copy.deepcopy(param)
                    type = detail_params['type']
                    del detail_params['type']
                    url = self.detail_url + self.preapre_detail_params(detail_params, project_id=ipo_item.project_id)
                    yield scrapy.Request(url=url, callback=self.parse_detail, meta={"item":ipo_item, "type": type, "ipo_obj": ipo_obj}, headers=self.detail_headers, cookies=self.detail_cookies)

            
            # 额外的爬虫信息，用于后续数据分析
            companyInfo['crawlSource'] = response.url
            
            current_time = self.get_current_time()
            companyInfo['crawlTime'] = current_time
            companyInfo['crawlTimeString'] = self.get_time_str(current_time)
    
        
        
        
        next_page = -1
        
        if currentPageNo < self.pageCount :
            next_page = currentPageNo + 1
        else:
            print('所有长度', len(self.ipo_map.keys()), self.totalCount)
            print('所有页数', self.pageCount)
            
            result = {
                'totalCount': self.totalCount,
                'startTime': self.start_time,
                'startTimeStr': self.start_time_str,
                'company': list(self.ipo_map.values())
            }
            
            result = str(json.dumps(result, ensure_ascii=False,indent=4)).encode()
            
            
            # 代码执行根目录是从运行目录开始，scrapy文件目录结构是 projectname/projectname/spiders,spider存放了所有的爬虫，scrapy运行的目录结构是projectname/projectname
            # 所以这里的文件路径计算规则只要在往上一层即可
            file_prefix = util.get_crawl_file_prefix(os.getcwd())
            
            
            filename = f'{file_prefix}-{self.name}.json'
            
            with open(filename, 'wb') as file:
                file.write(result)
                return None
        
        if next_page > 0:
            next_url = self.target_url + self.prepare_params(pageNo= next_page)
            yield scrapy.Request(next_url, callback=self.parse, headers=self.headers, cookies=self.cookies)

    def parse_detail(self, response):
        json_dict = jsonp.loads_jsonp(_jsonp=response.text)
        # 获取结果
        result = json_dict['result']
        ipo_item = response.meta['item']
        type = response.meta['type']
        ipo_obj = response.meta['ipo_obj']
        project_id = ipo_item.project_id
        
        if project_id not in self.company_detail_items:
            if type == self.detail_params[0]['type']:
                result = result[0]
            self.company_detail_items[project_id] = {
                "crawl_count": 1,
                type: result
            }

        else:
            if type == self.detail_params[0]['type']:
                result = result[0]
            self.company_detail_items[project_id][type] = result
            self.company_detail_items[project_id]["crawl_count"] += 1
            if(self.company_detail_items[project_id]["crawl_count"] == len(self.detail_params)):
                print('detail---start')
                detail_item = self.company_detail_items[project_id]
                companyInfo = detail_item[self.detail_params[0]['type']]
                company_item = CompanyItem()
                company_item.load_item(retrive_dict = companyInfo)
                
                #print(company_item.to_dict())
                items = []
                # 获取进程信息，顺序是从最开始到最新
                milestomeInfos = detail_item[self.detail_params[1]['type']]
                for milestomeInfo in milestomeInfos:
                    milestone_item = KCBCompanyMilestoneItem()
                    milestone_item.load_item(retrive_dict = milestomeInfo)
                    milestone_item.company_id = company_item.id
                    milestone_item.company_name = company_item.name
                    yield milestone_item
                    items.append(milestone_item.to_dict())
                    #print(milestone_item.to_dict())
                ipo_obj['milestones'] = items
                items = []
                # 获取进程信息，顺序是从最新到最老，所以进行reverse
                processInfos = detail_item[self.detail_params[2]['type']]
                processInfos.reverse()
                for processInfo in processInfos:
                    process_item = KCBCompanyProcessItem()
                    process_item.load_item(retrive_dict = processInfo)
                    process_item.company_id = company_item.id
                    process_item.company_name = company_item.name
                    items.append(process_item.to_dict())
                    yield process_item
                ipo_obj['processes'] = items
                items = []
                
                others = filter(lambda p: p['reasonDesc'] != '', processInfos)
                for other in others:
                    other_item = KCBCompanyOtherItem()
                    other_item.load_item(retrive_dict = other)
                    other_item.company_id = company_item.id
                    other_item.company_name = company_item.name
                    items.append(other_item.to_dict())
                    yield other_item
                ipo_obj['others'] = items
                items = []
                
                files = detail_item[self.detail_params[3]['type']]
                files = sorted(files, key = lambda f: (int(f['fileUpdateTime'])))
                for file in files:
                    file_item = KCBFileItem()
                    file_item.load_item(retrive_dict = file)
                    file_item.company_id = company_item.id
                    items.append(file_item.to_dict())
                    yield file_item
                    #print(file_item.to_dict())

                csrc_files = detail_item[self.detail_params[4]['type']]
                csrc_files = sorted(csrc_files, key = lambda f: (int(f['fileUpdTime'])))
                for file in csrc_files:
                    file_item = KCBFileItem()
                    file['auditStatus'] = KCB_STAGE.MUNICIPAL_PARTY_COMMITTEE.value
                    file_item.load_item(retrive_dict = objects.assign({}, companyInfo, file))
                    file_item.company_id = company_item.id
                    items.append(file_item.to_dict())
                    yield file_item
                ipo_obj['files'] = items
                self.ipo_map[ipo_item.project_id] = ipo_obj
                items = []
                print('detail---end')
        