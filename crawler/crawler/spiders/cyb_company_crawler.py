# -*- coding: utf-8 -*-

import urllib
import time
import datetime
import json
import copy
import os
import random
import math
from pydash import objects

import scrapy
from crawler.items.base import MarketCountItem
from crawler.items.cyb import CYBCompanyItem, CYBIPOItem, CYBFileItem, CYBCompanyMilestoneItem, CYBCompanyOtherItem, CYBIntermediaryItem, CYBIntermediaryPersonItem
from crawler.util.constant import COMPANY_TYPE, INTERMEDIARY_TYPE, STOCK_EXCHANGE_TYPE
from crawler.util import util
from crawler.util import decorator
from crawler.util.postgre import CYBPostgreConnector
# =============================================================================
# 获取创业板当前过会进程中的上市公司
# =============================================================================
class CYBCompanySpider(scrapy.Spider):
    name = "cyb_company"
    custom_settings = {'ITEM_PIPELINES': {'crawler.pipelines.CYBPipeline': 300}}
    
    download_all = False

    params = {
        "bizType": 1, # bizType枚举？
    }
    
# 请求page的参数=============================================================================
     
    pageSize = 100
     
    # pageNo = 0 # 从0开始计数
     
    pageCount = 0
# =============================================================================
    
    totalCount = 0
    
    start_time = 0
    
    start_time_str = ''
    
    
    headers = {
        "Referer": "https://listing.szse.cn/projectdynamic/ipo/",
        # "sec-ch-ua": '"(Not(A:Brand";v="8", "Chromium";v="99", "Google Chrome";v="99"',
        
    }
    
    
    target_url = 'https://listing.szse.cn/api/ras/projectrends/query'
    
    detail_url = 'https://listing.szse.cn/api/ras/projectrends/details'

    ipo_map = {}

    ipo_obj = {
        "company": {},
        "ipo": {},
        "milestones": [],
        "others": [],
        "files": [],

    }
    
    # @classmethod
    # def from_cralwer(cls, crawler, *args, **kwargs):
    #     spider = super(CYBCompanySpider, cls).from_crawler(crawler, *args, **kwargs)
    #     crawler.signal.connect(spider.spider_close, )
    
    @decorator.inject_config
    def __init__(self):
        self.connector = CYBPostgreConnector()

    def datestr_to_timestamp(self, datestr):
        date_time = datetime.datetime.strptime(datestr,'%Y-%m-%d')
        timestamp = math.ceil(datetime.datetime.timestamp(date_time.now()))
        return timestamp
   
    def get_current_time(self): 
        current_milli_time = lambda: int(round(time.time() * 1000))
        return current_milli_time()
    
    def get_time_str(self, milli_time):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(milli_time/1000)) 
    
    def prepare_params(self, pageNo):
        request_params = copy.deepcopy(self.params)
        
        # 补充参数
        
        request_params['pageIndex'] = pageNo
        
        request_params['pageSize'] = self.pageSize
        
        request_params['random'] = str(random.random())
        
        
        print('?' + urllib.parse.urlencode(request_params))
        
        return '?' + urllib.parse.urlencode(request_params)
    
    def start_requests(self):
        urls = [
            self.target_url
        ]
                
        for url in urls:
            url = url + self.prepare_params(pageNo = 0)
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)
            
            
    def parse(self, response): 
 
        # json.dumps(): 将Python数据编码（转换）为JSON数据；
        # json.loads(): 将JSON数据转换（解码）为Python数据;
        # json.dump(): 将Python数据编码并写入JSON文件；
        # json.load(): 从JSON文件中读取数据并解码。

        json_dict = json.loads(response.text)
        
        # 获取结果
        result = json_dict['data']
        if self.totalCount == 0:
            self.totalCount = json_dict['totalSize']
            count_item = MarketCountItem()
            count_info = {
                'count': self.totalCount,
                'stock_exchange_type':STOCK_EXCHANGE_TYPE.CYB.value
            }
            
            count_item.load_item(retrive_dict = count_info)
            yield count_item
                

        
        for companyInfo in result:

            ipo_item = CYBIPOItem()
            ipo_item.load_item(retrive_dict = companyInfo)
            
            # 写文件数据准备
            if ipo_item.project_id not in self.ipo_map.keys():                
                ipo_obj = copy.deepcopy(self.ipo_obj)
                ipo_obj['ipo'] = ipo_item.to_dict()
                self.ipo_map[ipo_item.project_id] = ipo_obj
            
            trigger_item_pipeline = False
            
            is_ipo_existed = self.connector.is_ipo_existed(project_id=ipo_item.project_id)
            trigger_item_pipeline = not is_ipo_existed
            
            is_ipo_updated = None
            if is_ipo_existed:
                is_ipo_updated = self.connector.is_ipo_updated(project_id=ipo_item.project_id, update_time=ipo_item.update_time, update_date=ipo_item.update_date)
                trigger_item_pipeline = is_ipo_updated
                print(f'is_ipo_existed:{is_ipo_existed}, is_ipo_updated:{is_ipo_updated}')
                
            

            if trigger_item_pipeline or self.download_all:
                print(ipo_item.to_dict())
                detail_params = {
                    "id": ipo_item.project_id,
                    "r": str(random.random())
                }
                url = self.detail_url + '?' + urllib.parse.urlencode(detail_params)
                yield scrapy.Request(url=url, callback=self.parse_detail,  headers=self.headers)

            companyInfo['crawlSource'] = response.url
            
            current_milli_time = lambda: int(round(time.time() * 1000))
            companyInfo['crawlTime'] = current_milli_time()
            companyInfo['crawlTimeString'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(current_milli_time()/1000)) 
    
        
        # result = sorted(result, key=lambda result: (-float(result['maramt']), result['stage'], result['prjstatus'], self.datestr_to_timestamp(datestr=result['updtdt'])))
        
        # 获取所有条数
        totalSize = int(json_dict['totalSize'])
        
        
        # 计算所有页数
        self.pageCount = math.ceil(totalSize / self.pageSize)
        
        currentPageNo = int(json_dict['pageIndex'])
        
        next_page = -1
        
        if currentPageNo + 1 < self.pageCount and len(result) > 0 :
            next_page = currentPageNo + 1
        else:
            print('所有长度', len(self.ipo_map.keys()), self.totalCount)
            print('所有页数', self.pageCount)
            
            # 1.状态、更新时间、申请金额
            # result = sorted(self.company, key=lambda result: (-float(result['maramt']), result['stage'], result['prjstatus'], self.datestr_to_timestamp(datestr=result['updtdt'])))
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
            
            print('filename: ', filename)
            
            with open(filename, 'wb+') as file:
                file.write(result)
                return None
        
        if next_page > 0:
            next_url = self.target_url + self.prepare_params(pageNo= next_page)
            yield scrapy.Request(next_url, callback=self.parse)

    def parse_detail(self, response):
        json_dict = json.loads(response.text)
        
        # 获取结果
        result = json_dict['data']

        items = []
        company_item = CYBCompanyItem()
        company_item.load_item(retrive_dict = result)
        company_item.csrc_company_type = COMPANY_TYPE.NORMAL.value
        yield company_item
        
        ipo_item = CYBIPOItem()
        ipo_item.load_item(retrive_dict = result)
        ipo_item.company_id = company_item.id
        yield ipo_item

        # 写文件数据准备
        ipo_obj = copy.deepcopy(self.ipo_obj)
        ipo_obj['ipo'] = ipo_item.to_dict()
        ipo_obj['company'] = company_item.to_dict()
        
        items = []
        person_items = []
        # 中介机构 及 中介人员
        intermediarys = [
            {
                "type": INTERMEDIARY_TYPE.ACCOUNTING_FIRM.value,
                "name": result['acctfm'],
                "person": map(lambda x: ({ "personName": x }), result['acctsgnt'].split('，'))

            },
            {
                "type": INTERMEDIARY_TYPE.LAW_FIRM.value,
                "name": result['lawfm'],
                "person": map(lambda x: ({ "personName": x }), result['lglsgnt'].split('，'))
            },
            {
                "type": INTERMEDIARY_TYPE.SPONSOR.value,
                "name": result['sprinst'],
                "person": map(lambda x: ({ "personName": x }), result['sprrep'].split('，'))
            },
            {
                "type": INTERMEDIARY_TYPE.ASSET_EVALUATION_INSTITUTE.value,
                "name": result['evalinst'],
                "person": map(lambda x: ({ "personName": x }), result['evalsgnt'].split('，'))
            },
        ]
        if result['jsprinst'] != '':
            intermediarys.append({
                "type": INTERMEDIARY_TYPE.RATING_AGENCY.value,
                "name": result['jsprinst'],
                "person": map(lambda x: ({ "personName": x }), result['jsprrep'].split('，'))
            })
        for intermediary in intermediarys:
            intermediary_item = CYBIntermediaryItem()
            intermediary_item.load_item(retrive_dict = objects.assign({}, result, intermediary))
            # intermediary_item.intermediary_id = str(uuid.uuid4())
            yield intermediary_item
            items.append(intermediary_item.to_dict())
            
            persons = intermediary['person']
            for person in persons:
                person_item = CYBIntermediaryPersonItem()
                person_item.load_item(retrive_dict = objects.assign({}, result, person ))
                person_item.intermediary_id = intermediary_item.intermediary_id
                # person_item.id = str(uuid.uuid4())
                yield person_item
                person_items.append(person_item.to_dict())
        
        
        items = []
        person_items = []
        
        print('进程文件')
        # result['disclosureMaterials'] = sorted(result['disclosureMaterials'], key = lambda f: (util.convert_time(f['ddtime'])))
        # result['disclosureMaterials'].reverse()
        for file in result['disclosureMaterials']:
            file_item = CYBFileItem()
            file_item.load_item(retrive_dict = file)
            file_item.company_id = company_item.id
            yield file_item
            items.append(file_item.to_dict())
        
        print('问询回复')
        for file in result['enquiryResponseAttachment']:
            file_item = CYBFileItem()
            file_item.load_item(retrive_dict = file)
            file_item.company_id = company_item.id
            yield file_item
            items.append(file_item.to_dict())
        
        print('上市委结果')
        for file in result['meetingConclusionAttachment']:
            file_item = CYBFileItem()
            file_item.load_item(retrive_dict = file)
            file_item.company_id = company_item.id
            yield file_item
            items.append(file_item.to_dict())
            
        
        print('证监会结果')
        sec_result_files = result['registrationResultAttachment'] + result['terminationNoticeAttachment']
        for file in sec_result_files:
            file_item = CYBFileItem()
            file_item.load_item(retrive_dict = file)
            file_item.company_id = company_item.id
            yield file_item
            items.append(file_item.to_dict())
        
        ipo_obj['files'] = items
        items = []

        # 创业板ipo进程数据
        target_progress = []
        progress = result['prjprogs']
        progress = sorted(progress, key = lambda p: (int(p['orderNo'])))

        if len(progress) > 0 and progress[0]['orderNo'] == -1:
            last_p = progress.pop(0)
            progress.append(last_p)
        for p in progress:
            status = p['status']
            del p['status']
            if any(str(s['value']) == str(p['value'])  for s in target_progress) == False:
                target_progress.append(p)
            
            if len(status) > 0:
                
                for s_p in status:
                    if any(str(s['value']) == str(s_p['value'])  for s in target_progress) == False:
                        target_progress.append(s_p)
                    
        for p in target_progress:
            milestone_item = CYBCompanyMilestoneItem()
            milestone_item.load_item(retrive_dict = p)
            milestone_item.company_id = company_item.id
            milestone_item.company_name = company_item.name
            milestone_item.project_id = ipo_item.project_id
            yield milestone_item
            items.append(milestone_item.to_dict())          
        
        ipo_obj['milestones'] = items
        items = []
        
        
        # IPO其他信息数据
        others = result['others']
        target_others = []
        if others != None and len(others) > 0:
            for other in others:
                for key,value in other.items():
                    target_others.append({
                        "date": key,
                        "reason": value
                    })
            target_others = sorted(target_others, key = lambda o: util.convert_time(o['date']))
            target_others.reverse()
            for other in target_others:
                other_item = CYBCompanyOtherItem()
                other_item.load_item(retrive_dict = other)
                other_item.company_id = company_item.id
                other_item.company_name = company_item.name
                other_item.project_id = ipo_item.project_id
                # other_item.id = str(uuid.uuid4())
                yield other_item
                items.append(other_item.to_dict())
        ipo_obj['others'] = items
        self.ipo_map[ipo_item.project_id] = ipo_obj
        items = []