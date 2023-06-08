# -*- coding: utf-8 -*-
import scrapy

from crawler.converter.sz_zbss import\
    project as project_converters,\
    process as process_converters


from crawler.spiders.sz_base_crawler import BaseSpider
# =============================================================================
# 获取获取深圳证券交易所当前过会进程中的所有公司（创业板和深圳主板）
# =============================================================================
class SZ_ZBSS_Spider(BaseSpider, scrapy.Spider):
    name = "sz_zbss"
    
    params = {
        "bizType": 5, # bizType枚举？
    }

    headers = {
        "Referer": "https://listing.szse.cn/projectdynamic/ntb/index.html",
        # "sec-ch-ua": '"(Not(A:Brand";v="8", "Chromium";v="99", "Google Chrome";v="99"',
        
    }
    
    project_converters = project_converters

    process_converters = process_converters
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SZ_ZBSS_Spider, cls).from_crawler(crawler, *args, **kwargs)

        # 注册 spider_opened 信号的处理方法，注入自定义逻辑
        crawler.signals.connect(spider.on_spider_opened, signal=scrapy.signals.spider_opened)
        return spider

    def start_requests(self):
        return super().start_requests()
            
            
    