# -*- coding: utf-8 -*-
import scrapy
import urllib
import time
import copy
import json
import copy
import os
from pydash import clone_deep,get

from crawler.items.loader import TableLoader
from crawler.util import decorator
from crawler.util import util
from crawler.util import jsonp

from crawler.converter.sh import\
      company_manager as company_manager_converters,\
      person as person_converters,\
      sh_intermediary_person as sh_intermediary_person_converters,\
      sh_intermediary as sh_intermediary_converters,\
      company as company_converters,\
      file as file_converters,\
      intermediary as intermediary_converters,\
        zjh_company as zjh_company_converters,\
        intermediary_company as intermediary_company_converters


class BaseSpider:
    table_loader = {}
    headers = {
        "Referer": "http://listing.sse.com.cn/"
    }
    # 注册制新增对象
    registry_params = {
        "issueMarketType": "1,2"
    }
    
    common_request_params = {
        "isPagination": True,
        "pageHelp.pageSize": 100,
        "offerType": '',
        "issueMarketType": "1,2",
        "currStatus": '',
        "order": 'updateDate|desc',
        "keyword": '',
        "auditApplyDateBegin": '',
        "auditApplyDateEnd": '',
        "_": round(time.time() * 1000),
    }

    cookies = {
        "yfx_c_g_u_id_10000042": "ck22022520090216302302193303981",
        "yfx_f_l_v_t_10000042": "f_t_1645790942421__r_t_1645790942421__v_t_1645790942421__r_c_0"
    }

    detail_headers = {
        "Referer": "http://listing.sse.com.cn/"
    }
    detail_cookies = {
        'yfx_c_g_u_id_10000042': '_ck21022121261410069772517758114',
         'yfx_f_l_v_t_10000042': 'f_t_1613913973987__r_t_1657514138370__v_t_1657514138370__r_c_9'
    }

    detail_url = 'http://query.sse.com.cn/commonSoaQuery.do'

    is_yield = True
    
    download_all = False

    pageCount = 0    
    
    totalCount = 0
    
    start_time = 0
    
    start_time_str = ''

    # 写入文件数据 start
    company = []
    company_items = {}
    
    company_detail = []
    company_detail_items = {}
    
    crawl_company_map = {}

    crawl_company_obj = {
        "company": {},
        "ipo": {},
        "milestones": [],
        "process": [],
        "others": [],
        "files": [],

    }
    # 写入文件数据 end

    @decorator.inject_config   
    def __init__(self, *args, **kwargs):
        # print('base init success')
        super().__init__(*args, **kwargs)
    
    def on_spider_opened(self):
        # 执行自定义逻辑
        # 在 spider_opened 信号的处理方法中获取配置参数
        base_dir = self.crawler.settings.get('BASE_DIR')
        self.table_loader = TableLoader(self.settings['BASE_DIR'])
        self.params = {
            **self.common_request_params,
            **self.params
        }


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
        
        # print('request_params', request_params)

        return '?' + urllib.parse.urlencode(request_params)

    def preapre_detail_params(self, detail_param, project_id, inject_params = True):
        params = copy.deepcopy(detail_param)
        if inject_params:
            params = { **self.registry_params, **params }
        params['stockAuditNum'] = project_id
        params['jsonCallBack'] = 'jsonCallback' + str(round(time.time() * 1000))
        params['_'] = self.get_current_time()
        params['isPagination'] = 'false'
        return '?' + urllib.parse.urlencode(params)

    def appendCralwInfo(self, companyInfo, url):
        companyInfo['crawlSource'] = url
        
        current_milli_time = lambda: int(round(time.time() * 1000))
        companyInfo['crawlTime'] = current_milli_time()
        companyInfo['crawlTimeString'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(current_milli_time()/1000)) 
        # print(companyInfo)
        return companyInfo
    
    def load_table(self, table_name):
        result_table = self.table_loader.load_table(scope = self.name, table_name=table_name)
        return result_table

    def start_requests(self):
        urls = [
            self.target_url
        ]
        
        self.start_time = self.get_current_time()
        self.start_time_str = self.get_time_str(self.start_time)
        

        for url in urls:
            url = url + self.prepare_params(pageNo = 1)
            return scrapy.Request(url=url, callback=self.parse, headers=self.headers, cookies=self.cookies)
    
    def parse(self, response): 
 
        json_dict = jsonp.loads_jsonp(_jsonp=response.text)
        
        
        # 获取结果
        result = json_dict['result']
        # 获取页码
        pageSetting = json_dict['pageHelp']
        
        # 获取所有页数
        self.pageCount = pageSetting['pageCount']
        
        marketTypeData = json_dict['marketTypeData']

        # self.totalCount = pageSetting['total']
        
        currentPageNo = pageSetting['pageNo']
        
        if self.totalCount == 0:
            if isinstance(marketTypeData, list):
                for market in marketTypeData:
                    # print('market', market)
                    self.totalCount = pageSetting['total']
                    count_table = self.load_table(table_name='MARKET_COUNT')
                    current_time = util.get_current_time()
                    current_date = util.get_time_str(current_time, '%Y-%m-%d')
                    count_table.load_record({
                        **market,
                        'count': market['num'],
                        'time': current_time,
                        'date': current_date
                    })
                    count_table.save()
        #origin = json_dict['origin']
        #print("公网ip: ",response.headers)
        
        for companyInfo in result:
            # 添加公司信息

            company_table = self.load_table(table_name='COMPANY')
            company_table.converters = company_converters
            [company_target_column, company_item] = company_table.load_record(companyInfo)
            company_table.save()
            
            zjh_company_table = self.load_table(table_name='ZJH_COMPANY')
            zjh_company_table.converters = zjh_company_converters
            zjh_company_table.load_record(companyInfo)
            zjh_company_table.save()
            
            project_table = self.load_table(table_name=self.name.upper())
            project_table.converters = self.project_converters
            [project_target_column, project_item] = project_table.load_record(companyInfo)
            is_project_existed = project_table.is_exist(companyInfo)
            # print('is_existed', is_project_existed)
            is_project_update = False
            if is_project_existed == True:
                is_project_update = project_table.is_updated(companyInfo, ['update_time','accept_apply_time'])
                # print('is_project_update', is_project_update)
            # if sh_ipo.is_exist(companyInfo) == True:

            # is_ipo_existed = self.connector.is_ipo_existed(project_id=ipo_item.project_id)
            # trigger_item_pipeline = not is_ipo_existed
            # is_ipo_updated = None
            # if is_ipo_existed:
            #     is_ipo_updated = self.connector.is_ipo_updated(project_id=ipo_item.project_id, update_time=ipo_item.update_time, update_date=ipo_item.update_date)
            #     trigger_item_pipeline = is_ipo_updated
            # else: 
            #     yield company_item


            # 写文件数据准备
            if project_item['project_id'] not in self.crawl_company_map.keys():   
                project_table.save()             
                crawl_company_obj = copy.deepcopy(self.crawl_company_obj)
                crawl_company_obj['ipo'] = clone_deep(project_item)
                crawl_company_obj['company'] = clone_deep(company_item)
                self.crawl_company_map[project_item['project_id']] = crawl_company_obj

            if not is_project_existed or is_project_update: # self.download_all 
                print('(not is_project_existed) or is_project_update', project_item['project_id'])
                # 写文件数据准备            
                crawl_company_obj = copy.deepcopy(self.crawl_company_obj)
                crawl_company_obj['ipo'] = clone_deep(project_item)
                crawl_company_obj['company'] = clone_deep(company_item)

                self.load_company_manager(companyInfo)

                intermediary_table = self.load_table(table_name='INTERMEDIARY')
                intermediary_table.converters = intermediary_converters
                
                sh_intermediary_table = self.load_table(table_name='SH_INTERMEDIARY')
                sh_intermediary_table.converters = sh_intermediary_converters

                sh_intermediary_person_table = self.load_table(table_name='SH_INTERMEDIARY_PERSON')
                sh_intermediary_person_table.converters = sh_intermediary_person_converters
                
                person_table = self.load_table(table_name='PERSON')
                person_table.converters = person_converters
                
                # 中介信息,循环生成
                intermediarys = companyInfo['intermediary']
                for intermediary in intermediarys:

                    intermediary_table.load_record({**intermediary, **companyInfo})
                    intermediary_table.save()
                    # print('intermediary', intermediary)
                    company_table.converters = intermediary_company_converters
                    company_table.load_record(intermediary)
                    company_table.save()

                    sh_intermediary_table.load_record({**intermediary, **companyInfo})
                    sh_intermediary_table.save()
                    
                    intermediary_persons = intermediary['i_person']
                    # 中介人员信息，循环生成
                    for intermediary_person in intermediary_persons:
                        # print('intermediary_person', intermediary_person)
                        sh_intermediary_person_table.load_record({**intermediary_person, **intermediary, **companyInfo})
                        sh_intermediary_person_table.save()
                        person_table.load_record(intermediary_person)
                        person_table.save()

                # 查询详情数据
                for param in self.detail_params:
                    detail_params = copy.deepcopy(param['params'])
                    type = param['type']
                    url = self.detail_url + self.preapre_detail_params(detail_params, project_id=project_item['project_id'], inject_params = param.get('inject_params', True))
                    yield scrapy.Request(url=url, callback=self.parse_detail, meta={"item":project_item, "type": type, "crawl_company_obj": crawl_company_obj}, headers=self.detail_headers, cookies=self.detail_cookies)

            
            # 额外的爬虫信息，用于后续数据分析
            companyInfo['crawlSource'] = response.url
            
            current_time = self.get_current_time()
            companyInfo['crawlTime'] = current_time
            companyInfo['crawlTimeString'] = self.get_time_str(current_time)
    
        next_page = -1
        
        if currentPageNo < self.pageCount :
            next_page = currentPageNo + 1
        else:
            print('所有长度', len(self.crawl_company_map.keys()), self.totalCount)
            print('所有页数', self.pageCount)
            
            result = {
                'totalCount': self.totalCount,
                'startTime': self.start_time,
                'startTimeStr': self.start_time_str,
                'company': list(self.crawl_company_map.values())
            }
            
            result = str(json.dumps(result, ensure_ascii=False,indent=4)).encode()
            
            
            # 代码执行根目录是从运行目录开始，scrapy文件目录结构是 projectname/projectname/spiders,spider存放了所有的爬虫，scrapy运行的目录结构是projectname/projectname
            # 所以这里的文件路径计算规则只要在往上一层即可
            file_prefix = util.get_crawl_file_prefix(os.getcwd())
            
            
            filename = f'{file_prefix}-{self.name}.json'
            
            # with open(filename, 'wb') as file:
            #     file.write(result)
            #     return None
        
        if next_page > 0:
            next_url = self.target_url + self.prepare_params(pageNo= next_page)
            yield scrapy.Request(next_url, callback=self.parse, headers=self.headers, cookies=self.cookies)

    def load_project(self, companyInfo):
        project = self.load_table(table_name=self.name.upper())
        project.converters = self.project_converters
        [project_target_column, project_item] = project.load_record(companyInfo)
        project.save()
        # print(companyInfo)
        # print(project.columns)
        # print(project_item)
        return project_item

    
    def load_company_manager(self,companyInfo):
        pass

    def parse_detail(self, response):
        json_dict = jsonp.loads_jsonp(_jsonp=response.text)
        # 获取结果
        result = json_dict['result']
        project_item = response.meta['item']
        type = response.meta['type']
        crawl_company_obj = response.meta['crawl_company_obj']
        project_id = project_item['project_id']
        
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
                # print('detail---start')
                detail_item = self.company_detail_items[project_id]
                companyInfo = detail_item[self.detail_params[0]['type']]
                
                #print(company_item.to_dict())
                items = []
                
                for detail_param in self.detail_params[1:]:
                    table_name = detail_param['table']
                    cur_type = detail_param['type']
                    converters = detail_param['converters']
                    sort = detail_param.get('sort', False)
                    sortField = detail_param.get('sortField', '')
                    table = self.load_table( table_name)
                    table.converters = converters
                    items = detail_item[cur_type]
                    
                    if sort == True and sortField != '':
                        items = sorted(items, key = lambda f: (int(f[sortField])))
                    
                    # 针对process的特殊处理
                    if cur_type == 'process':
                        items.reverse()
                        sh_other_table = self.load_table( table_name='SH_OTHER')
                        sh_other_table.converters = converters
                        others = filter(lambda p: p['reasonDesc'] != '', items)
                        for other in others:
                            sh_other_table.load_record({
                                **companyInfo,
                                **other
                                
                            })
                            sh_other_table.save()

                        crawl_company_obj['others'] = clone_deep(others)

                    # 针对 csrc_files 特殊处理
                    if cur_type == 'csrc_files':
                        enums = table.enums
                        audit_status = get(enums, 'IPO_STATUS.values.MUNICIPAL_PARTY_COMMITTEE.value')
                        for item in items:
                            item['auditStatus'] = audit_status
                            table.load_record({
                                **companyInfo,
                                **item
                            })
                            table.save()
                    else:
                        for item in items:
                            table.load_record({
                                **companyInfo,
                                **item
                            })
                            table.save()
                    
                    crawl_company_obj[cur_type] = items
                
                self.crawl_company_map[project_item['project_id']] = crawl_company_obj
                items = []
                # print('detail---end')
        