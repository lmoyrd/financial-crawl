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
      file as file_converters

from crawler.converter.sh_bgcz import\
    project as project_converters,\
    process as process_converters


from crawler.spiders.sh_base_crawler import BaseSpider

# from crawler.items import CrawlerItem

# =============================================================================
# 获取上海证券交易所当前过会进程中的所有公司（科创板和上海主板）
# 增量更新两个办法：1.是走sql，先find后插入；2.走redis，使用数据指纹（id+updateTime+stage+stage_status）走增量开发。
# =============================================================================
class SH_BGCZ_Spider(BaseSpider, scrapy.Spider):
    name = "sh_bgcz"

    target_url = 'http://query.sse.com.cn/bgczStatusAction.do'

    params = {
        # "jsonCallBack": 'jsonCallback' + str(round(time.time() * 1000)),
        
        "sqlId": 'GP_BGCZ_XMLB',
        "order": 'updateDate|desc,stockAuditNum|desc'
    }
    
    
    detail_params = [
        {
            'type': 'detail',
            "params": {
                'sqlId': 'GP_BGCZ_XMLB'
            },
            
        },
        {
            'type': 'milestone',
            "params": {
                'sqlId': 'GP_BGCZ_XMDTZTTLB'
            },
            'inject_params': False,
            'table': 'SH_MILESTONE',
            'converters': process_converters
        },
        {
            'type': 'progress',
            "params": {
                'sqlId': 'GP_BGCZ_XMZTYYLB',
                'order': 'operationTime|desc'
            },
            'inject_params': False,
            'table': 'SH_PROCESS',
            'converters': process_converters

        },
        {
            'type': 'files',
            "params": {
                'sqlId': 'GP_BGCZ_SSWHYGGJG'
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
        spider = super(SH_BGCZ_Spider, cls).from_crawler(crawler, *args, **kwargs)

        # 注册 spider_opened 信号的处理方法，注入初始化自定义逻辑，逻辑托管到BaseSpider
        crawler.signals.connect(spider.on_spider_opened, signal=scrapy.signals.spider_opened)
        return spider

    def start_requests(self):
        yield super().start_requests()