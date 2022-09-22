# -*- coding: utf-8 -*-
import scrapy
import urllib
import time
import datetime
import json
import copy
import os
from pydash import objects

from scrapy import signals
from itemloaders import ItemLoader
import attrs
from ..items.kcb import CompanyItem, IPOItem, CompanyManagerItem, IntermediaryItem, KCBIntermediaryItem, KCBIntermediaryPersonItem, KCBCompanyMilestoneItem, KCBCompanyProcessItem,KCBFileItem, KCBCompanyOtherItem
from ..util.constant import COMPANY_TYPE, KCB_STAGE
from ..util import util
from ..util import jsonp # 对应模块 ../util/jsonp.py, 模块加载是以脚本所在目录结构为根目录

# from crawler.items import CrawlerItem

# =============================================================================
# 获取科创板当前过会进程中的特定公司
# 代码可以和kcb_company_cralwer.py合并，去除冗余代码
# =============================================================================
class KCBCompanyDetailSpider(scrapy.Spider):
    

    # params = {
    #     # "jsonCallBack": 'jsonCallback' + str(round(time.time() * 1000)),
    #     "isPagination": True,
    #     "sqlId": 'SH_XM_LB',
    #     "pageHelp.pageSize": 100,
    #     # "pageHelp.pageNo": 1,
    #     "_": round(time.time() * 1000),
    #     "offerType": '',
    #     "commitiResult": '',
    #     "registeResult": '',
    #     "csrcCode": '',
    #     "currStatus": '',
    #     "province": '',
    #     "order": 'updateDate|desc',
    #     "keyword": '',
    #     "auditApplyDateBegin": '',
    #     "auditApplyDateEnd": '',
    # }
    
    
    pageCount = 0    
    
    totalCount = 0
    
    start_time = 0
    
    start_time_str = ''

    headers = {
        "Referer": "http://kcb.sse.com.cn/"
    }
    cookies = {
        'yfx_c_g_u_id_10000042': '_ck21022121261410069772517758114',
         'yfx_f_l_v_t_10000042': 'f_t_1613913973987__r_t_1657514138370__v_t_1657514138370__r_c_9'
    }

    url = 'http://query.sse.com.cn/commonSoaQuery.do'

    params = [
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
    
    result = {}

    crawl_count = 0
    
    project_id = 67

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(KCBCompanyDetailSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        return spider


    def spider_opened(self, spider):
        from_crawl = util.get_crawl()
        print('from_crawl', from_crawl)

    def get_current_time(self): 
        current_milli_time = lambda: int(round(time.time() * 1000))
        return current_milli_time()
    
    def get_time_str(self, milli_time):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(milli_time/1000)) 

    def prepare_params(self, detail_param):
        params = copy.deepcopy(detail_param)
        params['stockAuditNum'] = self.project_id
        params['jsonCallBack'] = 'jsonCallback' + str(round(time.time() * 1000))
        params['_'] = self.get_current_time()
        params['isPagination'] = False
        
        return '?' + urllib.parse.urlencode(params)

    # def __init__(self, stats):
    #     self.stats = stats

    # @classmethod
    # def from_crawler(cls, crawler):
    #     return cls(crawler.stats)

    def start_requests(self):
        

        for param in self.params:
            cur_param = copy.deepcopy(param)
            type = cur_param['type']
            del cur_param['type']
            url = self.url + self.prepare_params(cur_param)
            yield scrapy.Request(url=url, callback=self.parse_wrapper(type=type), headers=self.headers, cookies=self.cookies)

    def parse_wrapper(self, type):
        return lambda response: self.parse(response, type)    

    def parse(self, response, type): 
        
        json_dict = jsonp.loads_jsonp(_jsonp=response.text)
        # 获取结果
        result = json_dict['result']
        self.crawl_count += 1
        
        self.result[type] = result
        if type == self.params[0]['type']:
            self.result[type] = result[0]
            
        # elif type == self.params[1]['type']:

        if self.crawl_count == len(self.params):
            # 全部爬取完毕
            # 获取公司信息
            companyInfo = self.result[self.params[0]['type']]
            company_item = CompanyItem()
            company_item.load_item(retrive_dict = companyInfo)
            yield company_item

            company_managers = companyInfo['stockIssuer']
            for manager in company_managers:
                manager_item = CompanyManagerItem()
                manager_item.load_item(retrive_dict = manager)
                manager_item.company_id = company_item.id
                yield manager_item
            
            ipo_item = IPOItem()
            ipo_item.load_item(retrive_dict = companyInfo)
            ipo_item.company_id = company_item.id
            yield ipo_item
            
            intermediarys = companyInfo['intermediary']
            for intermediary in intermediarys:

                intermediary_item = IntermediaryItem()
                intermediary_item.load_item(retrive_dict = intermediary)
                yield intermediary_item
                #print(intermediary_item.to_dict())
                # yield intermediary_item
                intermediary_kcb_item = KCBIntermediaryItem()
                intermediary_kcb_item.load_item(retrive_dict = intermediary)
                yield intermediary_kcb_item
                # yield intermediary_kcb_item
                #print(intermediary_kcb_item.to_dict())
                intermediary_persons = intermediary['i_person']
                # 中介人员信息，循环生成
                for intermediary_person in intermediary_persons:
                    person_item = KCBIntermediaryPersonItem()
                    person_item.load_item(retrive_dict = objects.assign({}, intermediary_person, intermediary))
                    
                    yield person_item
            
            #print(company_item.to_dict())
            
            # 获取进程信息，顺序是从最开始到最新
            milestomeInfos = self.result[self.params[1]['type']]
            for milestomeInfo in milestomeInfos:
                milestone_item = KCBCompanyMilestoneItem()
                milestone_item.load_item(retrive_dict = milestomeInfo)
                milestone_item.company_id = company_item.id
                milestone_item.company_name = company_item.name
                yield milestone_item
                #print(milestone_item.to_dict())
            
            # 获取进程信息，顺序是从最新到最老，所以进行reverse
            processInfos = self.result[self.params[2]['type']]
            processInfos.reverse()
            for processInfo in processInfos:
                process_item = KCBCompanyProcessItem()
                process_item.load_item(retrive_dict = processInfo)
                process_item.company_id = company_item.id
                process_item.company_name = company_item.name
                yield process_item
            
            others = filter(lambda p: p['reasonDesc'] != '', processInfos)
            for other in others:
                other_item = KCBCompanyOtherItem()
                other_item.load_item(retrive_dict = other)
                other_item.company_id = company_item.id
                other_item.company_name = company_item.name
                yield other_item

            files = self.result[self.params[3]['type']]
            files = sorted(files, key = lambda f: (int(f['fileUpdateTime'])))
            for file in files:
                file_item = KCBFileItem()
                file_item.load_item(retrive_dict = file)
                file_item.company_id = company_item.id
                #print(file_item.to_dict())

            csrc_files = self.result[self.params[4]['type']]
            csrc_files = sorted(csrc_files, key = lambda f: (int(f['fileUpdTime'])))
            for file in csrc_files:
                file_item = KCBFileItem()
                file['auditStatus'] = KCB_STAGE.MUNICIPAL_PARTY_COMMITTEE.value
                file_item.load_item(retrive_dict = objects.assign({}, companyInfo, file))
                file_item.company_id = company_item.id
                yield file_item
            # return None
            result = str(json.dumps(self.result, ensure_ascii=False,indent=4)).encode()
            # 代码执行根目录是从运行目录开始，scrapy文件目录结构是 projectname/projectname/spiders,spider存放了所有的爬虫，scrapy运行的目录结构是projectname/projectname
            # 所以这里的文件路径计算规则只要在往上一层即可
            file_prefix = util.get_crawl_file_prefix(os.getcwd())
            filename = f'{file_prefix}-{self.name}.json'
            
            with open(filename, 'wb') as file:
                file.write(result)
                return None
        # else:
            
            