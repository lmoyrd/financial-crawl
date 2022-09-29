

import argparse
import filetype
import os
import re
import urllib.request
import pdfplumber

from copy import deepcopy
from common import pdfparser
from common.postgre import ZBPostgreConnector

""" 获取数据库中当前最新的pdf数据
select  distinct on(a.company_name)  *
from (
	SELECT company_name, file_name, file_type_of_process_desc, publish_time from "ZB_FILE" order by publish_time desc
) a ) b order by b.publish_time desc;
使用任务去解析pdf数据，而不阻塞爬虫数据
"""

def file_name(file_dir):
    L=[]
    for i,j,files in os.walk(file_dir):
        L=files
    return L


def connect_db():
    return ZBPostgreConnector()


argv_parser = argparse.ArgumentParser()

'''
runfile('文件路径', args='-t="10:56"', wdir='文件路径')
'''
argv_parser.add_argument('-pa','--parse-all', default=False, type=bool, help='是否强制抓取所有数据，默认为否，只更新有变更的数据')

if __name__ == '__main__':

    args = argv_parser.parse_args()
    # Namespace => dict
    # args_dict = vars(args)
    parse_all = args.parse_all

    # 先找到所有为0的IPO数据
    connector = connect_db()
    # 不对，如果有更新也需要重跑
    if parse_all == True:
        ipos = connector.get_all_ipos()
    else:
        ipos = connector.get_empty_ipo()

    path=os.path.abspath(os.path.join(os.getcwd(), "../temp/files"))
    files=file_name(path)
    error_files = []
    for index, ipo in enumerate(ipos):
        
        [lastest_file, *others] = connector.get_ipo_lasted_file(ipo['project_id'])
        if lastest_file != None:
            ipo_file_name = lastest_file['file_name']
            file_url = lastest_file['file_url']
            print(ipo_file_name, file_url)
            file_path = os.path.join(path, ipo_file_name)
            if ipo_file_name not in files:
                print(f'{ipo_file_name}需要下载')
                url = urllib.request.urlopen(file_url)
                file = open(os.path.join(path, ipo_file_name), 'wb')
                block_sz = 8192
                while True:
                    buffer = url.read(block_sz)
                    if not buffer:
                        break
                    file.write(buffer)
                file.close()
                print('下载成功')
            
            total_fund_rasing = pdfparser.parse_pdf(file_path)
            
            if 560 > total_fund_rasing > 0:
                
                clone_ipo = deepcopy(ipo)
                clone_ipo['total_fund_rasing'] = total_fund_rasing
                connector.update_ipo(clone_ipo, 'total_fund_rasing')

                print(f'总计{len(ipos)} 当前进度 {index + 1}; ',ipo['project_id'], f'募资{total_fund_rasing}亿元')
            else: 
                error_files.append({
                    'company_name': ipo['project_id'],
                    'total_fund_rasing': total_fund_rasing,
                })
                print(f'总计{len(ipos)} 当前进度 {index + 1}; ',ipo['project_id'], f'募资{total_fund_rasing}亿元')
    if len(error_files) > 0:
        print(error_files)
        print(f'解析成功：{len(ipos) - len(error_files)}, 失败：{len(error_files)}, 解析失败率：{len(error_files) / len(ipos)}')

    # path=os.path.abspath(os.path.join(os.getcwd(), "../temp/files"))
    # files=file_name(path)
    # print(len(files))
    # for i in range(len(files)):
    #     file_path = os.path.join(path, files[i])
        
    #     # if '新湖期货股份有限公司', '浙江峻和科技股份有限公司', '苏州新大陆精密科技股份有限公司', '开源证券股份有限公司', '中路交科科技股份有限公司'
    #     # if '上海金标文化创意股份' in file_path:
    #     if '大陆精密科技' in file_path:
    #         print(file_path)
    #         pdfparser.parse_pdf(file_path)
    #     # kind = filetype.guess(os.path.join(path, files[i]))
    #     # if kind is not None and kind.extension == 'pdf':
    #     #     print(file_path)
    #     #     pdfparser.parse_pdf(file_path)
            
