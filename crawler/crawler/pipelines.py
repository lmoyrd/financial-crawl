# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import psycopg2
import psycopg2.extras
import scrapy
import urllib
import time
import redis
import os
import hashlib

from io import BytesIO
from scrapy.utils.project import get_project_settings
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.misc import md5sum
from twisted.internet.defer import Deferred, inlineCallbacks
from itemadapter import ItemAdapter
from scrapy.http import Request
from urllib.parse import urlparse
from os.path import basename, dirname, join
from os.path import splitext



# import asyncio
# import aiohttp
# import aiofiles

from .util import util
from crawler.util.postgre import  ZBPostgreConnector

# loop = asyncio.get_event_loop() 

# sema = asyncio.BoundedSemaphore(5)

# async def fetch_file(url, filename):
#     async with sema, aiohttp.ClientSession() as session:
#         async with session.get(url) as resp:
#             assert resp.status == 200
#             data = await resp.read()

#     async with aiofiles.open(
#         filename, "wb"
#     ) as outfile:
#         await outfile.write(data)
    
# pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
# r = redis.Redis(connection_pool=pool)

class BasePipeline:
    connector = None
    item_to_func = {}
    def process_item(self, item, spider):
        
        item_dict = item.to_dict()
        # 获得item name
        item_type = type(item).__name__
        if item_type in self.item_to_func.keys():
            func_name = self.item_to_func[item_type]
            if func_name != '' and hasattr(self.connector, f'insert_or_update_{func_name}') and hasattr(self.connector[f'insert_or_update_{func_name}'], '__call__'):
                self.connector[f'insert_or_update_{func_name}'](item_dict)
                self.connector.commit()

class ZBFilePipeline(FilesPipeline):
    project_settings = get_project_settings()
    base_file_path = project_settings.attributes['FILES_STORE'].value
    base_absolute_path = os.path.abspath(os.path.join(os.getcwd(), base_file_path))
    def file_path(self, request, response=None, info=None, *, item=None):
        file_name = None
        if item != None:
            item_dict = item.to_dict()
            file_name = item_dict['file_name']

        return file_name if file_name != None else ''
    
    # def item_completed(self, results, item, info):
    #     if item is not None:
    #         item_type = type(item).__name__
    #         # 下载pdf文件，解析其中的募集资金
    #         if item_type == 'ZBIPOItem':
    #             file_paths = [x['path'] for ok, x in results if ok]
    #             file_path = file_paths[0]
    #             # pdfparser.parse_pdf(os.path.join(self.base_absolute_path,file_path))
    #     return item
    
    # def media_downloaded(self, response, request, info, *, item=None):
    #     print('media_downloaded')
    #     buf = BytesIO(response.body)
    #     buf.seek(0)
    #     pdfparser.parse_pdf_by_buffer(buf)
    #     # 进行pdf解析
    #     return super().media_downloaded(response, request, info, item)
    
    def get_media_requests(self, item, info):
        if item is not None:
            item_type = type(item).__name__
            # 下载pdf文件，解析其中的募集资金
            if item_type == 'ZBIPOItem':
                item_dict = item.to_dict()
                file_url = item_dict['file_url']
                if file_url:
                    yield scrapy.Request(file_url, meta={"ipo_item": item})
                # for file_url in adapter['file_urls']:
                #     yield scrapy.Request(file_url)
    

class ZBPipeline(BasePipeline):
    item_to_func = {
        # 主板
        "ZBIPOItem" : "ipo",        
        "ZBCompanyProcessItem": "process",
        "ZBFileItem": "file",
        "MarketCountItem" : "count",
    }
    connector = ZBPostgreConnector()
        # super().process_item(item, spider)