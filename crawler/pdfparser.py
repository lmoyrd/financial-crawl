from copy import deepcopy
import filetype
import os
import re
import urllib.request
import pdfplumber
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



if __name__ == '__main__':
    # 先找到所有为0的IPO数据
    connector = connect_db()
    # 不对，如果有更新也需要重跑
    ipos = connector.get_empty_ipo()

    path=os.path.abspath(os.path.join(os.getcwd(), "../temp/files"))
    files=file_name(path)

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
            
            if total_fund_rasing > 0:
                
                clone_ipo = deepcopy(ipo)
                clone_ipo['total_fund_rasing'] = total_fund_rasing
                connector.update_ipo(clone_ipo, 'total_fund_rasing')

                print(f'总计{len(ipos)} 当前进度 {index}; ',ipo['project_id'], f'募资{total_fund_rasing}亿元')

                
                

    # path=os.path.abspath(os.path.join(os.getcwd(), "../temp/files"))
    # files=file_name(path)
    # print(len(files))
    # for i in range(len(files)):
    #     file_path = os.path.join(path, files[i])
        
    #     # if '新湖期货股份有限公司', '浙江峻和科技股份有限公司', '苏州新大陆精密科技股份有限公司', '开源证券股份有限公司', '中路交科科技股份有限公司'
    #     # if '上海金标文化创意股份' in file_path:
    #     if '郑州三晖电气股份有限公司' in file_path:
    #         print(file_path)
    #         pdfparser.parse_pdf(file_path)
    #     # kind = filetype.guess(os.path.join(path, files[i]))
    #     # if kind is not None and kind.extension == 'pdf':
    #     #     print(file_path)
    #     #     pdfparser.parse_pdf(file_path)
            
