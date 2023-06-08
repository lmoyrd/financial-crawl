# -*- coding: utf-8 -*-
import scrapy
import urllib
import time
import datetime
import json
import copy
import os
import random
import math
from pydash import objects,clone_deep,get


from crawler.items.loader import TableLoader

from crawler.util import util
from crawler.util import decorator
from crawler.converter.sz import\
    zjh_company as zjh_company_converters,\
    person as person_converters,\
    file as file_converters,\
    company as company_converters,\
    intermediary as intermediary_converters,\
    intermediary_company as intermediary_company_converters,\
    sz_intermediary_person as sz_intermediary_person_converters,\
    sz_intermediary as sz_intermediary_converters
    # company_manager as company_manager_converters,\

# =============================================================================
# 获取获取深圳证券交易所当前过会进程中的所有公司（创业板和深圳主板）
# =============================================================================
class BaseSpider():
    
    download_all = False

    params = {
        "bizType": 1, # bizType枚举？
    }

    common_request_params = {}
    
# 请求page的参数=============================================================================
     
    pageSize = 100
     
    # pageNo = 0 # 从0开始计数
     
    pageCount = 0
# =============================================================================
    
    totalCount = 0
    
    start_time = 0
    
    start_time_str = ''
    
    
    target_url = 'https://listing.szse.cn/api/ras/projectrends/query'
    
    detail_url = 'https://listing.szse.cn/api/ras/projectrends/details'

    project_map = {}

    project_obj = {
        "company": {},
        "ipo": {},
        "milestones": [],
        "others": [],
        "files": [],

    }

    enums = {}
    
    @decorator.inject_config   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    
    def on_spider_opened(self):
        # 执行自定义逻辑
        # 在 spider_opened 信号的处理方法中获取配置参数
        base_dir = self.crawler.settings.get('BASE_DIR')
        self.table_loader = TableLoader(self.settings['BASE_DIR'], self.remove_all or False)
        self.params = {
            **self.common_request_params,
            **self.params
        }

    def datestr_to_timestamp(self, datestr):
        date_time = datetime.datetime.strptime(datestr,'%Y-%m-%d')
        timestamp = math.ceil(datetime.datetime.timestamp(date_time.now()))
        return timestamp
   
    def get_current_time(self): 
        current_milli_time = lambda: int(round(time.time() * 1000))
        return current_milli_time()
    
    def get_time_str(self, milli_time):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(milli_time/1000)) 
    
    def load_table(self, table_name):
        result_table = self.table_loader.load_table(scope = self.name, table_name=table_name)
        return result_table

    def prepare_params(self, pageNo):
        request_params = copy.deepcopy(self.params)
        
        # 补充参数
        
        request_params['pageIndex'] = pageNo
        
        request_params['pageSize'] = self.pageSize
        
        request_params['random'] = str(random.random())
        
        return '?' + urllib.parse.urlencode(request_params)
    
    def start_requests(self):
        urls = [
            self.target_url
        ]
        count_table = self.load_table(table_name='MARKET_COUNT')
        # 拿到dbjson中的枚举值
        self.enums = count_table.enums
        issue_market = get(self.enums, 'ISSUE_MARKET.values')   
        for url in urls:
            if isinstance(issue_market, dict):
                for key, obj in issue_market.items():
                    value = obj.get('value', None)
                    if value != None:
                        target_url = url + self.prepare_params(pageNo = 0) + f'&boardCode={value}'
                        yield scrapy.Request(url=target_url, callback=self.parse, meta={"issue_market_code":value, "first_load": True}, headers=self.headers)

    def parse(self, response): 
 
        # json.dumps(): 将Python数据编码（转换）为JSON数据；
        # json.loads(): 将JSON数据转换（解码）为Python数据;
        # json.dump(): 将Python数据编码并写入JSON文件；
        # json.load(): 从JSON文件中读取数据并解码。
        json_dict = json.loads(response.text)
        issue_market_code = response.meta['issue_market_code']
        first_laod = response.meta.get('first_load', False)
        # 获取结果
        result = json_dict['data']
        if first_laod == True:
            self.totalCount = json_dict['totalSize']
            count_table = self.load_table(table_name='MARKET_COUNT')
            current_time = util.get_current_time()
            current_date = util.get_time_str(current_time, '%Y-%m-%d')
            [column, record] = count_table.load_record({
                'boardCode': issue_market_code,
                'count': self.totalCount,
                'time': current_time,
                'date': current_date
            })
            count_table.save()
        
        for companyInfo in result:
            
            project_table = self.load_table(table_name=self.name.upper())
            project_table.converters = self.project_converters
            project_item = project_table.load_record(companyInfo)[-1]
            is_project_existed = project_table.is_exist(companyInfo)
            # print('is_existed', is_project_existed)
            is_project_update = False
            if is_project_existed == True:
                is_project_update = project_table.is_updated(companyInfo, ['update_time','accept_apply_time'])
                # print('is_project_update', is_project_update)

            
            # # 写文件数据准备
            if project_item['project_id'] not in self.project_map.keys():                
                project_obj = copy.deepcopy(self.project_obj)
                project_obj['ipo'] = clone_deep(project_item)
                self.project_map[project_item['project_id']] = project_obj
            
                
            

            if (not is_project_existed) or is_project_update:
                print('(not is_project_existed) or is_project_update', project_item['project_id'])
                detail_params = {
                    "id": project_item['project_id'],
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
            print('所有长度', len(self.project_map.keys()), self.totalCount)
            print('所有页数', self.pageCount)
            
            # 1.状态、更新时间、申请金额
            # result = sorted(self.company, key=lambda result: (-float(result['maramt']), result['stage'], result['prjstatus'], self.datestr_to_timestamp(datestr=result['updtdt'])))
            result = {
                'totalCount': self.totalCount,
                'startTime': self.start_time,
                'startTimeStr': self.start_time_str,
                'company': list(self.project_map.values())
            }
            
            result = str(json.dumps(result, ensure_ascii=False,indent=4)).encode()
            
            # 代码执行根目录是从运行目录开始，scrapy文件目录结构是 projectname/projectname/spiders,spider存放了所有的爬虫，scrapy运行的目录结构是projectname/projectname
            # 所以这里的文件路径计算规则只要在往上一层即可
            file_prefix = util.get_crawl_file_prefix(os.getcwd())
            
            
            filename = f'{file_prefix}-{self.name}.json'
            
            print('filename: ', filename)
            
            # with open(filename, 'wb+') as file:
            #     file.write(result)
            #     return None
        
        if next_page > 0:
            next_url = self.target_url + self.prepare_params(pageNo= next_page) + f'&boardCode={issue_market_code}'
            yield scrapy.Request(url=next_url, callback=self.parse, meta={"issue_market_code":issue_market_code, "first_load": False}, headers=self.headers)

    def parse_detail(self, response):
        json_dict = json.loads(response.text)
        
        # 获取结果
        result = json_dict['data']
        companyInfo = result
        items = []
        
        project_table = self.load_table(table_name=self.name.upper())
        project_table.converters = self.project_converters
        project_table.clear()
        project_item = project_table.load_record(companyInfo)[-1]
        # if str(project_item['issue_market']) == '12':
        # print('project_item', project_item)
        # print(companyInfo)
        project_table.save()

        company_table = self.load_table(table_name='COMPANY')
        company_table.converters = company_converters
        company_item = company_table.load_record(companyInfo)[-1]
        # print('company_item', company_item)
        company_table.save()
        
        zjh_company_table = self.load_table(table_name='ZJH_COMPANY')
        zjh_company_table.converters = zjh_company_converters
        zjh_company_item = zjh_company_table.load_record(companyInfo)[-1]
        # print('zjh_company_item', zjh_company_item)
        zjh_company_table.save()
        
        
        # 写文件数据准备
        project_obj = copy.deepcopy(self.project_obj)
        project_obj['ipo'] = clone_deep(project_item)
        project_obj['company'] = clone_deep(company_item)
        
        items = []
        person_items = []
        # 中介机构 及 中介人员
        intermediarys = [
            {
                "type": get(self.enums, 'INTERMEDIARY_TYPE.values.ACCOUNTING_FIRM.value'),
                "name": result['acctfm'],
                "code": '',
                "person_field": 'acctsgnt',
            },
            {
                "type": get(self.enums, 'INTERMEDIARY_TYPE.values.LAW_FIRM.value'),
                "name": result['lawfm'],
                "code": '',
                "person_field": 'lglsgnt',
            },
            {
                "type": get(self.enums, 'INTERMEDIARY_TYPE.values.SPONSOR.value'),
                "name": result['sprinst'],
                "code": result['sprcd'],
                "person_field": 'sprrep',
            }
        ]
        if result['jsprinst'] != '':
            intermediarys.append({
                "type": get(self.enums, 'INTERMEDIARY_TYPE.values.SUB_SPONSOR.value'),
                "name": result['jsprinst'],
                "code": result['jsprcd'],
                "person_field": 'jsprrep',
            })
        
        # 特殊处理资产评估机构
        if type(result['evalinst']) == str and result['evalinst'] != '':
            if '，' in result['evalinst']:
                # print('evalinst', result['evalinst'])
                # print('evalsgnt', result['evalsgnt'])
                # 证明是有多个资产评估机构，其person字段是按照<br />区分，内部按照，字符区分。按照此规则处理
                eval_list = result['evalinst'].split('，')
                eval_person_list = result['evalsgnt'].split('<br />')
                for index, eval_item in enumerate(eval_list):
                    # eval_person_item = map(lambda x: ({ "personName": x }), eval_person_list[index].split('，')) if type(eval_person_list[index]) == str else []
                    # print('eval_item, ', eval_item)
                    # print('eval_person_item', eval_person_list[index])
                    # 出现index out of range
                    intermediarys.append({
                        "type": get(self.enums, 'INTERMEDIARY_TYPE.values.ASSET_EVALUATION_INSTITUTE.value'),
                        "name": eval_item,
                        "code": '',
                        "source_person": eval_person_list[index]
                    })

            else:
                intermediarys.append({
                    "type": get(self.enums, 'INTERMEDIARY_TYPE.values.ASSET_EVALUATION_INSTITUTE.value'),
                    "name": result['evalinst'],
                    "code": '',
                    "person_field": 'evalsgnt',
                })
        
        for intermediary in intermediarys:
            source_person = ''
            if 'source_person' in intermediary:
                source_person = intermediary['source_person']
            else:
                person_field = intermediary['person_field']
                source_person = result[person_field]
            intermediary['person'] = map(lambda x: ({ "personName": x }), source_person.split('，')) if len(source_person.split('，')) > 0 else []

        intermediary_table = self.load_table(table_name='INTERMEDIARY')
        intermediary_table.converters = intermediary_converters
        
        sz_intermediary_table = self.load_table(table_name='SZ_INTERMEDIARY')
        sz_intermediary_table.converters = sz_intermediary_converters

        sz_intermediary_person_table = self.load_table(table_name='SZ_INTERMEDIARY_PERSON')
        sz_intermediary_person_table.converters = sz_intermediary_person_converters
        
        person_table = self.load_table(table_name='PERSON')
        person_table.converters = person_converters
        intermediarys = list(filter(lambda x: x['name'] != '', intermediarys))
        for intermediary in intermediarys:
            
            intermediary_record = intermediary_table.load_record({**companyInfo, **intermediary})[-1]
            # print('INTERMEDIARY', intermediary_record)
            intermediary_table.save()
            
            company_table.converters = intermediary_company_converters
            intermediary_company = company_table.load_record(intermediary)[-1]
            # print('intermediary_company', intermediary_company)
            company_table.save()

            sz_intermediary_record = sz_intermediary_table.load_record({**companyInfo,**intermediary,})[-1]
            sz_intermediary_table.save()
            # print('sz_intermediary_record', sz_intermediary_record)
            
            
            intermediary_persons = intermediary['person']
            for intermediary_person in intermediary_persons:
                if intermediary_person['personName'] != None and intermediary_person['personName'] != '':
                    
                    # print('intermediary_person', intermediary_person)
                    sz_intermediary_person = sz_intermediary_person_table.load_record({**companyInfo, **intermediary_person, **intermediary})[-1]
                    if 'source_person' in intermediary:
                        print('sz_intermediary_person', sz_intermediary_person)
                    sz_intermediary_person_table.save()
                    
                    
                    person = person_table.load_record(intermediary_person)[-1]
                    # print('person', person)
                    person_table.save()

        
        
        items = []
        person_items = []
        
        result['disclosureMaterials'] = sorted(result['disclosureMaterials'], key = lambda f: (util.convert_time(f['ddtime'])))
        result['disclosureMaterials'].reverse()
        file_table = self.load_table(table_name='SZ_FILE')
        file_table.converters = file_converters
        for file in result['disclosureMaterials']:
            if file['dfpth'] != None and file['dfpth'] != '':
                file_record = file_table.load_record({
                    **file,
                    **companyInfo,
                })[-1]
                file_table.save()
                # print('SZ_FILE', file, file_record)
        
        for file in result['enquiryResponseAttachment']:
            if file['dfpth'] != None and file['dfpth'] != '':
                file_record = file_table.load_record({
                    **file,
                    **companyInfo,
                })[-1]
                file_table.save()
                # print('SZ_FILE_2', file, file_record)
        
        for file in result['meetingConclusionAttachment']:
            if file['dfpth'] != None and file['dfpth'] != '':
                file_record = file_table.load_record({
                    **file,
                    **companyInfo,
                })[-1]
                file_table.save()
                # print('SZ_FILE_3', file, file_record)
            # file_item = SZ_IPO_FileItem()
            # file_item.load_item(retrive_dict = file)
            # file_item.company_id = company_item.id
            # yield file_item
            # items.append(file_item.to_dict())
            
        
        sec_result_files = result['registrationResultAttachment'] + result['terminationNoticeAttachment']
        for file in sec_result_files:
            if file['dfpth'] != None and file['dfpth'] != '':
                file = file_table.load_record({
                    **file,
                    **companyInfo,
                })[-1]
                file_table.save()
            # print('SZ_FILE_4', file)
        
        if result['ntbListedResultAttachment'] != None and len(result['ntbListedResultAttachment']) > 0:
            for file in result['ntbListedResultAttachment']:
                if file['dfpth'] != None and file['dfpth'] != '':
                    file_record = file_table.load_record({
                        **file,
                    **companyInfo,
                    })[-1]
                    file_table.save()
                    # print('SZ_FILE_5', file, file_record)

        # project_obj['files'] = items
        # items = []

        # 深交所进程数据
        process_table = self.load_table(table_name='SZ_MILESTONE')
        process_table.converters = self.process_converters


        target_progress = []
        progress = result['prjprogs']
        progress = sorted(progress, key = lambda p: (int(p['orderNo'])))
        last_p = None
        if len(progress) > 0 and progress[0]['orderNo'] == -1:
            last_p = progress.pop(0)
        
        # 去除其他未完成的进程项
        progress = list(filter(lambda x: x['finished'] != False, progress))
        
        # print('filter process', progress)
        for p in progress:
            status = p['status']
            del p['status']
            target_progress.append(p)
            # if any(str(s['value']) == str(p['value']) and p['finished'] == True  for s in target_progress) == False:
            #     target_progress.append(p)
            
            # if len(status) > 0:
                
            #     for s_p in status:
            #         # 未完成不添加
            #         if any(str(s['value']) == str(s_p['value']) and s_p['finished'] ==True  for s in target_progress) == False:
            #             target_progress.append(s_p)
        
        # TODO: 有问题在修正；深交所的process很诡异，不知道为何要这么返回，总之，只筛选finished为true的值，但是还存在提交注册 注册结果等stage_status同时存在False和True的item，这个时候，这里就以有True的为准，简单处理。
        if last_p != None:
            try:
                result_status = [pro for i, pro in enumerate(target_progress) if str(pro['value']) == str(last_p['value'])] or [None]
                # if len(result_status)  == 1:
                #     print('111result_status', result_status)
                #     print('last_p', last_p)
                #     print('target_progress', target_progress)
                #     print('origin process', result['prjprogs'])
                #     print('\n')
                if len(result_status) == 1 and result_status[0] == None:
                    target_progress.append(last_p)
                    
            except Exception as e:
                # pass
                print('e target_progress', e)
                print('target_progress', target_progress)
                print('last_p', last_p)

        target_progress = sorted(target_progress, key = lambda p: (int(p['orderNo'])))          
        # print('target_progress', target_progress)
        for p in target_progress:
            # milestone_item = milestone_table.load_record({
            #     **companyInfo,
            #     **p
            # })[-1]
            # print('milestone_item', milestone_item)
            process_item = process_table.load_record({
                **companyInfo,
                **p
            })[-1]
            process_table.save()
            # print('process_item', process_item)
 
        
        project_obj['milestones'] = items
        items = []
        
        
        # # # IPO其他信息数据
        others = result['others']
        target_others = []
        sz_other_table = self.load_table( table_name='SZ_OTHER')
        sz_other_table.converters = self.process_converters
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
                other_record = sz_other_table.load_record({
                    **other,
                    **companyInfo,
                })[-1]
                # print('other_record', other_record)
                sz_other_table.save()
        project_obj['others'] = items
        items = []         