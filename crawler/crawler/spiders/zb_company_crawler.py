# -*- coding: utf-8 -*-

from copy import deepcopy

import scrapy
from urllib.parse import quote
import time
import datetime
import json
import os
import re

# from crawler.items import CrawlerItem

# import sys
# sys.path.append('..')
#from crawler.util import util
from crawler.util import decorator
from crawler.util import util
from crawler.util.constant import STOCK_EXCHANGE_TYPE
from crawler.items.base import MarketCountItem
from crawler.items.zb import ZBIPOItem, ZBCompanyProcessItem, ZBFileItem
from crawler.util.postgre import ZBPostgreConnector
# =============================================================================
# 获取当前过会进程中的公司
# 1.数据整理：
# 以公司名为核心，以时间为顺序，以状态为标准，对所有数据进行排序，
# company:
# 募资资金
#    status: 
#       date: [ downloadInfos:{ downloadInfoName, downloadUrl, downloadFileType, infoType } ]
# 先筛选所有company，然后使用keyword进行搜索，再进行解析，以获取最大量的company数据
# 主板只有预披露和预披露更新两种状态，且文件只有招股说明书，所以这部分简单了，就是需要对招股说明书进行解析
# 2.募资数据解析：只有招股说明书才进行pdf解析
# 
# =============================================================================
class EIDBaseCompanySpider(scrapy.Spider):
    name = 'zb_company'

    download_all = True
    custom_settings = {'ITEM_PIPELINES': 
        {
            'crawler.pipelines.ZBFilePipeline': 100,
            'crawler.pipelines.ZBPipeline': 300
        }
    }
    # user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.45 Safari/537.36"
    """
    页面请求参数:
    {
        prodType3: 
        prodType4: 
        keyWord: 
        keyWord2: 关键字
        selBoardCode: 
        selCatagory2: 
        startDate: 
        startDate2: 请输入开始时间
        endDate: 
        endDate2: 请输入结束时间
    }
    类型 formdata
    method: POST
    """
    
    currentPage = 0
    
    pageCount = 50 # 页面只提供50页
    
    totalCount = 0 # 所有公司数量
    
    headers = {
        "Referer": "http://eid.csrc.gov.cn",
        "Content-Type": "application/x-www-form-urlencoded"
        
    }
    
    cookies = {
        "yfx_c_g_u_id_10008998": "_ck22020821523616379948135356623",
        "yfx_f_l_v_t_10008998": "f_t_1644328356627__r_t_1644328356627__v_t_1644328356627__r_c_0",
        "BIGipServerpool_new_JJPL_8080": "2826962954.36895.0000",
        "acw_tc": "6f06f32416476152194455768e065b68a32d793583ea6dfa70b20e33f7"
    }
    
    # target_url = 'http://eid.csrc.gov.cn/ipo/1010/index'
    
    host = 'http://eid.csrc.gov.cn'
    
    stocks = [
        # 上海主板id
        '101010',
        # 深圳主板id
        '101011'
    ]
    target_template_url = 'http://eid.csrc.gov.cn/ipo/%s/index'

    stock_map = {
        stocks[0]: {
            'stock_exchange_type':STOCK_EXCHANGE_TYPE.SH_ZB.value,
            'stock_exchange_desc':STOCK_EXCHANGE_TYPE.SH_ZB.desc,
            'issue_market': 2,
            'issue_market_desc': '主板',
            'business_type': 1,
            'business_type_desc': 'IPO'
        },
        stocks[1]: {
            'stock_exchange_type': STOCK_EXCHANGE_TYPE.SZ_ZB.value,
            'stock_exchange_desc':STOCK_EXCHANGE_TYPE.SZ_ZB.desc,
            'issue_market': 12,
            'issue_market_desc': '主板',
            'business_type': 1,
            'business_type_desc': 'IPO'
        }
    }

    # 存放上海主板和深圳主板的数据, key为上海主板和深圳主板的url，value是company对象数组
    result_company = {
        stocks[0]: [],
        stocks[1]: [],
    }

    result_company_count = {
        stocks[0]: 0,
        stocks[1]: 0,
    }

    result_download_page = {
        stocks[0]: 0,
        stocks[1]: 0,
    }
    params = {
        stocks[0]: {
            "prodType3": "",
            "prodType4": "",
            "keyWord": "",
            "keyWord2": "关键字",
            "selBoardCode": "",
            "selCatagory2": '9601',
            "startDate": "",
            "startDate2": "请输入开始时间",
            "endDate": "",
            "endDate2": "请输入结束时间"
        },
        stocks[1]: {
            "prodType3": "",
            "prodType4": "",
            "keyWord": "",
            "keyWord2": "关键字",
            "selBoardCode": "",
            "selCatagory2": '9973',
            "startDate": "",
            "startDate2": "请输入开始时间",
            "endDate": "",
            "endDate2": "请输入结束时间"
        },
    }
    


    company = []
    
    target_company = []
    
    start_time = 0
    
    start_time_str = ''
    
    @decorator.inject_config
    def __init__(self):
        self.connector = ZBPostgreConnector()

    def get_current_time(self): 
        current_milli_time = lambda: int(round(time.time() * 1000))
        return current_milli_time()
    
    def get_time_str(self, milli_time):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(milli_time/1000)) 
    
    def prepare_params(self, url, pageNo):
        return f'{url}_{pageNo}.html'
    
    def start_requests(self):
                
        self.start_time = self.get_current_time()
        self.start_time_str = self.get_time_str(self.start_time)
        
        for stock in self.stocks:
            base_url = self.target_template_url % (stock)
            for value in range(1, self.pageCount + 1):
                url = f'{base_url}_{value}.html'
                yield scrapy.Request(url=url, callback=self.parse, meta={"stock": stock, "page": value}, headers=self.headers, cookies=self.cookies)

    def parse(self, response):
        meta = dict(response.meta)
        [stock, page, *others] = meta.values()
        self.result_download_page[stock] = page
        count = self.default_format(response.css('.g-ul'))
        self.result_company_count[stock] = re.search(r'\d+',count).group()
        
        trs = response.css('.m-table2').xpath('./tr[@style!=\'\']')
        for index, tr in enumerate(trs):
            tds = tr.xpath('td')
            if len(tds) >= 6:
                company_name = self.default_format(tds[0])
                if company_name not in self.result_company[stock]:
                    self.result_company[stock].append(company_name)
        
        [page_sh_count, page_sz_count] = self.result_download_page.values()
        if page_sh_count == self.pageCount and page_sz_count == self.pageCount:
            current_time = util.get_current_time()
            # 公司total值
            for stock, count in self.result_company_count.items():
                count_item = MarketCountItem()
                count_info = {
                    **self.stock_map[stock],
                    'count': count,
                    'time': current_time,
                    'date': util.get_time_str(current_time, '%Y-%m-%d')
                }
                
                count_item.load_item(retrive_dict = count_info)
                yield count_item

            for stock, companys in self.result_company.items():
                base_url = self.target_template_url % (stock)
                for company in companys:
                    url = f'{base_url}_f.html'
                    params = deepcopy(self.params[stock])
                    params['keyWord'] = company
                    yield scrapy.FormRequest(url=url, method = 'POST', formdata = params, callback=self.parse_company, meta={"stock": stock, "company": company}, headers=self.headers, cookies=self.cookies)
                

    
    def default_format(self, target_element):
         if target_element.xpath != None:
             return target_element.xpath('./text()').get().strip().replace(' '
     , '')
         else:
             return ''
    
    def stock_company_format(self, target_element):
        if target_element.xpath != None:
            stock_companys = target_element.xpath('li/text()').getall()
            stock_companys = [item.strip().replace(' ','') for item in
     stock_companys]
            stock_company = ','.join(stock_companys)
            return stock_company
        else:
            return ''
    
    def attr_format(self, target_element):
         if target_element.xpath != None:
             attribute = target_element.xpath('@title').get()
             attribute = attribute.strip().replace(' ','')
             return attribute
         else:
             return ''
    
    def parse_download_url(self, url, name, time, local, file_type): 
        if url == '':
            return ''
        #print(url)
        lastIndex = url.rindex('.')
        real_file_type = url[lastIndex+1:]
        encode_url = quote(url)
        test_url_re = re.search(r'(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?', url)
        test_url = ''
        if test_url_re != None:
            try:
                test_url = test_url_re.group()
            except:
                test_url = ''
        
        if real_file_type == 'txt':
            target_url = url.replace('mnt', 'sr')
            target_url = f'{self.host}/{local}/txt.html?url={target_url}&name={name}&time={time}'
            #print(target_url)
            return quote(target_url)
        elif real_file_type == 'xbrl':
            target_url = f'http://xbrl.seid.com.cn/REPORT/{encode_url}'
            #print(target_url)
            return target_url
        elif test_url != '':
            return test_url
        else:
            return f'{self.host}{encode_url}'
    
    def get_str_btw(self, s, f, b):
        first_index = s.index(f)
        last_index = s.rindex(b)
        return s[first_index+1:last_index]
    
    def parse_company(self, response):
        meta = dict(response.meta)
        [stock, company, *others] = meta.values()
        self.currentPage += 1
        
        count = self.default_format(response.css('.g-ul'))
        self.totalCount = re.search(r'\d+',count).group()
        
        trs = response.css('.m-table2').xpath('./tr[@style!=\'\']')
        
        ipo_item = ZBIPOItem()
        ipo_info = {}

        file_items = []
        process_items = []
        for index, tr in enumerate(trs):
            tds = tr.xpath('td')
            
            if len(tds) >= 6:
                companyInfo = {}
                companyInfoFields = [
                    'company_name', 
                    'stage_name', 
                    'issue_market_desc', 
                    'sponsor_name', 
                    'update_date', 
                    'file_type_of_audit_desc',
                ]
                
                formaters=[
                    self.default_format,
                    self.default_format,
                    self.default_format,
                    self.stock_company_format,
                    self.default_format,
                    self.attr_format
                ]
                
                for i in range(0, 6):
                    formater = formaters[i]
                    text = formater(target_element=tds[i])
                    companyInfo[companyInfoFields[i]] = text
                
                # 额外的自定义信息
                pdf = tr.xpath('./@onclick').get()
                
                # 解析pdf字符信息
                pdf_arguments_str = self.get_str_btw(s = pdf, f = '(', b = ')')
                
                pdf_arguments = pdf_arguments_str.replace('\'','').split(',')
                
                if len(pdf_arguments) < 5:
                    print(companyInfo)
                [url, name, time, local, file_type] = pdf_arguments
                
                pdf_url = self.parse_download_url(*pdf_arguments)
                
                companyInfo['file_ext'] = file_type
                companyInfo['file_url'] = pdf_url
                companyInfo['file_type_of_process_desc'] = companyInfo['stage_name']
                companyInfo['publish_date'] = time
                file_name = f'{name}.{file_type}'
                company_name = companyInfo['company_name']
                
                if company_name != '' and company_name not in file_name:
                    companyInfo['file_name'] =f'{company_name}_{file_name}'
                else:
                    companyInfo['file_name'] = file_name
                
                file_item = ZBFileItem()
                file_item.load_item(retrive_dict = companyInfo)
                file_items.append(file_item)
                # yield file_item
                
                process_item = ZBCompanyProcessItem()
                process_item.load_item(retrive_dict = companyInfo)
                process_items.append(process_item)
                # yield process_item
                
                # IPO item
                if len(trs) > 1:
                    if index == 0:
                        ipo_info = companyInfo
                    elif index == len(trs) - 1:
                        ipo_info['create_date'] = companyInfo['update_date']
                        ipo_item.load_item(retrive_dict = ipo_info)

                        is_ipo_existed = self.connector.is_ipo_existed(project_id=ipo_item.project_id)
                        
                        
                        return self.update_ipo(ipo_item, process_items, file_items)
                        
                        # yield ipo_item
                        
                else:
                    if index == 0:
                        ipo_item = ZBIPOItem()
                        companyInfo['create_date'] = companyInfo['update_date']
                        ipo_item.load_item(retrive_dict = companyInfo)
                        return self.update_ipo(ipo_item, process_items, file_items)
                        # yield ipo_item

    def update_ipo(self, ipo_item, process_items, file_items):
        
        is_ipo_existed = self.connector.is_ipo_existed(project_id=ipo_item.project_id)
        trigger_item_pipeline = not is_ipo_existed
        is_ipo_updated = None
        if is_ipo_existed:
            is_ipo_updated = self.connector.is_ipo_updated(project_id=ipo_item.project_id, update_time=ipo_item.update_time, update_date=ipo_item.update_date)
            trigger_item_pipeline = is_ipo_updated
            print(f'is_ipo_existed:{trigger_item_pipeline}, is_ipo_updated:{is_ipo_updated}')
        
        if trigger_item_pipeline or self.download_all:
            print(f'is_ipo_updated:{is_ipo_updated}, {ipo_item.to_dict()}')
            yield ipo_item
            for file_item in file_items:
                yield file_item
            for process_item in process_items:
                yield process_item
