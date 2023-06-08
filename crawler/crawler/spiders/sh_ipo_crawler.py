# -*- coding: utf-8 -*-

import scrapy
import urllib
import time
import datetime
import json
import copy
import os
from pydash import clone_deep,get

from crawler.util import util
from crawler.util import jsonp # 对应模块 ../util/jsonp.py, 模块加载是以脚本所在目录结构为根目录


from crawler.converter.sh import\
      company_manager as company_manager_converters,\
      person as person_converters,\
      file as file_converters

from crawler.converter.sh_ipo import\
    project as project_converters,\
    process as process_converters

from crawler.spiders.sh_base_crawler import BaseSpider

# from crawler.items import CrawlerItem

# =============================================================================
# 获取上海证券交易所当前过会进程中的所有公司（科创板和上海主板）
# 增量更新两个办法：1.是走sql，先find后插入；2.走redis，使用数据指纹（id+updateTime+stage+stage_status）走增量开发。
# =============================================================================
class SH_IPO_Spider(BaseSpider, scrapy.Spider):
    name = "sh_ipo"

    target_url = 'http://query.sse.com.cn/statusAction.do'

    params = {
        # "jsonCallBack": 'jsonCallback' + str(round(time.time() * 1000)),
        "sqlId": 'SH_XM_LB',
        "commitiResult": '',
        "registeResult": '',
        "csrcCode": '',
        "province": '',
    }

    detail_params = [
        {
            'type': 'detail',
            #'jsonCallBack': 'jsonpCallback17952076'
            "params": {
                'sqlId': 'SH_XM_LB',
            },
            #stockAuditNum: 1045
            #_: 1657514175909
        },
        {
            'type': 'milestone',
            #jsonCallBack: jsonpCallback54987988
            "params": {
                'sqlId': 'GP_GPZCZ_XMDTZTTLB',
            },
            'inject_params': False,
            'table': 'SH_MILESTONE',
            'converters': process_converters
        },
        {
            'type': 'progress',
            "params": {
                'sqlId': 'GP_GPZCZ_XMDTZTYYLB',
                'order': 'qianDate|desc',
            },
            'inject_params': False,
            'table': 'SH_PROCESS',
            'converters': process_converters
        },
        {
            'type': 'files',
            "params": {
                'sqlId': 'GP_GPZCZ_SHXXPL',
            },
            'table': 'SH_FILE',
            'sort': True,
            'sortField': 'fileUpdateTime',
            'converters': file_converters
        },
        {
            'type': 'csrc_files',
            "params": {
                'sqlId': 'GP_GPZCZ_SSWHYGGJG',
                'fileType': '1,2,3,4',
            },
            'table': 'SH_FILE',
            'sort': True,
            'sortField': 'fileUpdTime',
            'converters': file_converters
        }
    ]
    
    project_converters = project_converters

    process_converters = process_converters

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SH_IPO_Spider, cls).from_crawler(crawler, *args, **kwargs)

        # 注册 spider_opened 信号的处理方法，注入自定义逻辑
        crawler.signals.connect(spider.on_spider_opened, signal=scrapy.signals.spider_opened)
        return spider

    def start_requests(self):
        yield super().start_requests()
    
    # @classmethod
    # def from_crawler(cls, crawler):
    #     return cls(crawler.stats)
    
    def load_company_manager(self,companyInfo): 
        company_manager = self.load_table(table_name='COMPANY_MANAGER')
        company_manager.converters = company_manager_converters
        person_table = self.load_table(table_name='PERSON')
        person_table.converters = person_converters
        # 公司高管信息
        company_managers = companyInfo['stockIssuer']
        for manager in company_managers:
            company_manager.load_record({**manager, **companyInfo})
            company_manager.save()
            
            person_table.load_record(manager)
            person_table.save()

    # def parse_detail(self, response):
    #     json_dict = jsonp.loads_jsonp(_jsonp=response.text)
    #     # 获取结果
    #     result = json_dict['result']
    #     project_item = response.meta['item']
    #     type = response.meta['type']
    #     crawl_company_obj = response.meta['crawl_company_obj']
    #     project_id = project_item['project_id']
        
    #     if project_id not in self.company_detail_items:
    #         if type == self.detail_params[0]['type']:
    #             result = result[0]
    #         self.company_detail_items[project_id] = {
    #             "crawl_count": 1,
    #             type: result
    #         }

    #     else:
    #         if type == self.detail_params[0]['type']:
    #             result = result[0]
    #         self.company_detail_items[project_id][type] = result
    #         self.company_detail_items[project_id]["crawl_count"] += 1
    #         if(self.company_detail_items[project_id]["crawl_count"] == len(self.detail_params)):
    #             print('detail---start')
    #             detail_item = self.company_detail_items[project_id]
    #             companyInfo = detail_item[self.detail_params[0]['type']]
                
    #             #print(company_item.to_dict())
    #             items = []

                
    #             sh_milestone_table = self.load_table( table_name='SH_MILESTONE')
    #             sh_milestone_table.converters = self.process_converters
    #             # 获取进程信息，顺序是从最开始到最新
    #             milestoneInfos = detail_item[self.detail_params[1]['type']]
    #             for milestoneInfo in milestoneInfos:
    #                 sh_milestone_table.load_record({
    #                     **companyInfo,
    #                     **milestoneInfo
    #                 })
    #                 sh_milestone_table.save()
    #                 #print(milestone_item.to_dict())
    #             crawl_company_obj['milestones'] = items


    #             sh_progress_table = self.load_table( table_name='SH_PROCESS')
    #             sh_progress_table.converters = self.process_converters

    #             items = []
    #             # 获取进程信息，顺序是从最新到最老，所以进行reverse
    #             processInfos = detail_item[self.detail_params[2]['type']]
    #             processInfos.reverse()
    #             for processInfo in processInfos:
    #                 sh_progress_table.load_record({
    #                     **companyInfo,
    #                     **processInfo
    #                 })
    #                 sh_progress_table.save()
                
    #             crawl_company_obj['processes'] = items
    #             items = []
                
    #             sh_other_table = self.load_table( table_name='SH_OTHER')
    #             sh_other_table.converters = self.process_converters
    #             others = filter(lambda p: p['reasonDesc'] != '', processInfos)
    #             for other in others:
    #                 sh_other_table.load_record({
    #                     **companyInfo,
    #                     **other
                        
    #                 })
    #                 sh_other_table.save()

    #             crawl_company_obj['others'] = items
    #             items = []
                
    #             sh_file_table = self.load_table( table_name='SH_FILE')
    #             sh_file_table.converters = file_converters

    #             files = detail_item[self.detail_params[3]['type']]
    #             files = sorted(files, key = lambda f: (int(f['fileUpdateTime'])))
    #             for file in files:
    #                 sh_file_table.load_record({
    #                     **companyInfo,
    #                     **file
    #                 })
    #                 sh_file_table.save()
    #                 #print(file_item.to_dict())
    #             try:
    #                 csrc_files = detail_item[self.detail_params[4]['type']]
    #                 csrc_files = sorted(csrc_files, key = lambda f: (int(f['fileUpdTime'])))
                    
    #                 enums = sh_file_table.enums
    #                 audit_status = get(enums, 'IPO_STATUS.values.MUNICIPAL_PARTY_COMMITTEE.value')
                    
    #                 for file in csrc_files:
    #                     file['auditStatus'] = audit_status
    #                     sh_file_table.load_record({
    #                         **companyInfo,
    #                         **file
    #                     })
    #                     sh_file_table.save()
    #             except Exception as e:
    #                 pass
    #             crawl_company_obj['files'] = items
    #             self.crawl_company_map[project_item['project_id']] = crawl_company_obj
    #             items = []
    #             print('detail---end')
        