# -*- coding: utf-8 -*-

import scrapy
import uuid
import urllib
import time
import datetime
import json
import copy
import os
import random
import math
from pydash import objects

from scrapy import signals
from itemloaders import ItemLoader
import attrs
from ..items.cyb import CYBCompanyItem, CYBIPOItem, CYBFileItem, CYBCompanyMilestoneItem, CYBCompanyOtherItem, CYBIntermediaryItem, CYBIntermediaryPersonItem
from ..util.constant import COMPANY_TYPE, INTERMEDIARY_TYPE
from ..util import util

# =============================================================================
# 获取创业板当前过会进程中的上市公司
# =============================================================================
class CYBCompanyDetailSpider(scrapy.Spider):
    

    params = {
        "id": 1002219,
    }
    start_time = 0
    
    start_time_str = ''
    
    
    headers = {
        "Referer": "https://listing.szse.cn/projectdynamic/ipo/",
        # "sec-ch-ua": '"(Not(A:Brand";v="8", "Chromium";v="99", "Google Chrome";v="99"',
        
    }
    
    
    target_url = 'https://listing.szse.cn/api/ras/projectrends/details'
    
    result = {}
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CYBCompanyDetailSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        return spider


    def spider_opened(self, spider):
        from_crawl = util.get_crawl()
        if from_crawl == '':
            util.set_crawl(spider.name)
        print('curr_crawl', util.get_crawl())

    def prepare_params(self):
        request_params = copy.deepcopy(self.params)
        
        request_params['r'] = str(random.random())
        
        return '?' + urllib.parse.urlencode(request_params)
    
    def start_requests(self):
        urls = [
            self.target_url
        ]
                
        for url in urls:
            url = url + self.prepare_params()
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)
            
            
    def parse(self, response): 
        
        now = datetime.datetime.now()
        
        filename_prefix = now.strftime('%Y-%m-%d %H-%M-%S')
 
        # json.dumps(): 将Python数据编码（转换）为JSON数据；
        # json.loads(): 将JSON数据转换（解码）为Python数据;
        # json.dump(): 将Python数据编码并写入JSON文件；
        # json.load(): 从JSON文件中读取数据并解码。

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
            intermediary_item.intermediary_id = str(uuid.uuid4())
            yield intermediary_item
            items.append(intermediary_item)
            print(intermediary_item.to_dict())
            persons = intermediary['person']
            for person in persons:
                person_item = CYBIntermediaryPersonItem()
                person_item.load_item(retrive_dict = objects.assign({}, result, person ))
                person_item.intermediary_id = intermediary_item.intermediary_id
                person_item.id = str(uuid.uuid4())
                yield person_item
                items.append(person_item)
                print(person_item.to_dict())
        print('进程文件')
        # result['disclosureMaterials'] = sorted(result['disclosureMaterials'], key = lambda f: (util.convert_time(f['ddtime'])))
        # result['disclosureMaterials'].reverse()
        for file in result['disclosureMaterials']:
            file_item = CYBFileItem()
            file_item.load_item(retrive_dict = file)
            file_item.company_id = company_item.id
            yield file_item
            items.append(file_item)
            print(file_item.to_dict())
        
        print('问询回复')
        for file in result['enquiryResponseAttachment']:
            file_item = CYBFileItem()
            file_item.load_item(retrive_dict = file)
            file_item.company_id = company_item.id
            yield file_item
            items.append(file_item)
            print(file_item.to_dict())
        
        print('上市委结果')
        for file in result['meetingConclusionAttachment']:
            file_item = CYBFileItem()
            file_item.load_item(retrive_dict = file)
            file_item.company_id = company_item.id
            yield file_item
            items.append(file_item)
            
            print(file_item.to_dict())
        
        print('证监会结果')
        sec_result_files = result['registrationResultAttachment'] + result['terminationNoticeAttachment']
        for file in sec_result_files:
            file_item = CYBFileItem()
            file_item.load_item(retrive_dict = file)
            file_item.company_id = company_item.id
            yield file_item
            items.append(file_item)
            print(file_item.to_dict())
        
        
        print('\n')

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
            items.append(milestone_item)
            print(milestone_item.to_dict())                
        
        
        # IPO其他信息数据
        others = result['others']
        target_others = []
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
            other_item.id = str(uuid.uuid4())
            yield other_item
            print(other_item.to_dict())
            items.append(other_item)

        items.insert(0, company_item)
        items.insert(0, ipo_item)
        print(company_item.to_dict(), ipo_item.to_dict())                
        dicts = [item.to_dict() for item in items]
        
        result = str(json.dumps(dicts, ensure_ascii=False,indent=4)).encode()
        # 代码执行根目录是从运行目录开始，scrapy文件目录结构是 projectname/projectname/spiders,spider存放了所有的爬虫，scrapy运行的目录结构是projectname/projectname
        # 所以这里的文件路径计算规则只要在往上一层即可
        file_prefix = util.get_crawl_file_prefix(os.getcwd())
        filename = f'{file_prefix}-{self.name}.json'
        
        # with open(filename, 'wb') as file:
        #     file.write(result)
        #     return None
        return None
        