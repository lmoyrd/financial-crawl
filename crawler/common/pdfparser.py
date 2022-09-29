# -*- coding: utf-8 -*-

# import filetype
import os
import re
import pdfplumber

from enum import Enum
from typing import Any, Callable

class BaseEnum(Enum):
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Enum):
            return self.value == other.value
    def __new__(cls, value, desc):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.desc = desc
        return obj

class PdfParserErrorEnum(BaseEnum):
    """
    pdf解析失败的类型汇总。
    toc解析失败：未解析到目录首页、未解析到目录尾页、未找到募资金额页
    募资资金解析失败：未找到募资表格，募资表格没有募资金额列，募资表格没有募资金额
    其他错误
    """
    UNFIND_TOC_START_PAGE = (-1, '未解析到目录首页')
    UNFIND_TOC_END_PAGE = (-2, '未解析到目录尾页')
    UNFIND_TOC_TOTAL_FUND_PAGE = (-3, '未找到募资金额页')
    
    
    UNFIND_TOTAL_FUND_TABLE = (-4, '未找到募资表格')
    UNFIND_TOTAL_FUND_TABLE_ROW = (-5, '募资表格没有募资金额列')
    TOTAL_FUND_NOT_IN_TABLE =  (-6, '募资表格没有募资金额')

    UNABLE_TO_BUILD_TOC = (-7, '未能构建目录')

    OTHER_ERROR = (-888, '其他错误')

class PdfParserError():
    """
    错误类型结构：
        错误类型
        错误内容
        错误上下文
    """
    type = ''
    message = ''
    context = {
        'page_number': '',
        'word': '',
    }
    def __init__(self, type, message, context = {}) -> None:
        self.type = type
        self.message = message
        self.context = context
        pass
    def __str__(self):
        return "错误类型: {0}, 错误信息: {1}, 错误上下文: {2}".format(self.type, self.message, self.context)

class PdfParserErrorBuilder():
    errors = []
    file_name = ''
    def set_filename(self, file_name) -> None:
        self.file_name = file_name
    
    def create_error(self, error: PdfParserError):
        self.errors.append(error)
    
    def log_error(self):
        if len(self.errors) > 0:
            print(f'{self.file_name}找不到募资金额,有如下错误')
            for error in self.errors:
                print(str(error))

pdfparse_error_builder = PdfParserErrorBuilder()

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    
    try:
        int(s)
        return True
    except ValueError:
        pass
    
    return False

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        pass
    
    return False

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    
    return False

def convert_to_int(s):
    try:
        int(s)
        return int(s)
    except ValueError:
        pass
    
    return None

def convert_to_number(s):
    try:
        float(s)
        return float(s)
    except ValueError:
        pass
    
    try:
        int(s)
        return int(s)
    except ValueError:
        pass
    
    return None


def filter_map(word):
    return word['text']




def find_number(word, default_number = None):
    if is_int(word):
        return int(word)
    
    word_reg = re.search(r'(\.|·{2,}?)(\d+$)', word)
    if word_reg is not None:
        word_group = word_reg.groups()
        (*other, page_number) = word_group
        return int(page_number) if is_number(page_number) else default_number
    return default_number
        

def get_tables_from_page(page):
    table_settings={
        # 存在表格没有边框的情况，这种情况就没法解析了，设置了这个属性也没用。如苏州新大陆精密科技股份有限公司
        'edge_min_length': 0,
    }
    tables = page.find_tables(table_settings={
         # 把募资金额的table的line宽度搞宽一些，但是架不住有错误的
        'snap_tolerance':12,

    })

    if len(tables) == 0 :
        tables = page.find_tables(table_settings=table_settings)

    return tables

def get_funding_rasing_number_from_footer(table_footer):
    billion_number = -1
    all_counts = [item for (index, item) in enumerate(table_footer) if item != None and is_number(item.replace(',',''))]
    print(all_counts)
    # 第二遍，取数逻辑
    # 数据优先级先取美制数字10,000 ；再取带小数位19.00；最后取整数
    counts = [item for (index, item) in enumerate(all_counts) if ',' in item]

    if len(counts) == 0:
        counts = [item for (index, item) in enumerate(all_counts) if is_float(item)]
        if len(counts) == 0:
            counts = [item for (index, item) in enumerate(all_counts) if is_int(item)]

    if len(counts) > 0:
        # 取数逻辑
        counts = list(map(lambda x: convert_to_number(x.replace(',','')), counts))
        if len(counts) > 0:
            # 一般在最后一个数字，找最后一个数字返回
            target_count = round(counts[-1] / 10000, 3)
            print('target_count', target_count)
            if 1 > target_count > 0:
                billion_number = counts[-1]
            else:
                billion_number = target_count  
    return billion_number

def get_fund_raise_number_in_next_page(page):
    billion_number = -1
    tables = get_tables_from_page(page)
    if len(tables) > 0:
        # 第一个table是募资资金表
        table_rows = tables[0].extract()
        print('rasing', table_rows)
        target_rows_index = -1
        for index, table_row in enumerate(table_rows):
            # 合计或总计
            target_rows_index = [index for (index, item) in enumerate(table_row) if item != None and item.replace(' ','').replace('\n', '').find('合计') > -1]
            target_rows_index = index if len(target_rows_index) > 0 else -1
        
        if target_rows_index > -1:
            footer = table_rows[target_rows_index]
        else:
            footer = table_rows[-1]

        billion_number = get_funding_rasing_number_from_footer(footer)
        # 第一个table是募资资金表
        # table = tables[0].extract()
    return billion_number

def get_fund_raise_number(fund_rasing_page, index, pdf):
    billion_number = -1
    tables = get_tables_from_page(fund_rasing_page)

    if len(tables) > 0:
        # 第一个table是募资资金表
        table = tables[0].extract()
        header = table[0]
        header_list = [item for (index, item) in enumerate(header) if item != None]
        if len(header_list) == 1:
            header = table[1]
        #header = table[1]
        footer = table[-1]
        
        # 可以通过lambda表达式拿到所有的index，且如下的(lambda)可以拿回类似js中的yield，执行next，有值就拿回
        target_indexs = (index for (index, item) in enumerate(header) if item != None and item.replace(' ','').replace('\n', '').find('募集资金') > -1)
        target_indexs_count = [index for (index, item) in enumerate(header) if item != None and item.replace(' ','').replace('\n', '').find('募集资金') > -1]

        if len(target_indexs_count) == 0:
            pdfparse_error_builder.create_error(PdfParserError(
                PdfParserErrorEnum.UNFIND_TOTAL_FUND_TABLE_ROW.value,
                PdfParserErrorEnum.UNFIND_TOTAL_FUND_TABLE_ROW.desc,
                {
                    'page_number': fund_rasing_page.page_number,
                    'table': table,
                    'header': header
                }
            ))   

        target_index = -1
        # 合计或总计
        footer_has_count = [index for (index, item) in enumerate(footer) if item != None and item.replace(' ','').replace('\n', '').find('合计') > -1]

        try:
            while billion_number == -1:
                target_index = next(target_indexs)
                if len(header) == len(footer) and target_index > 0 and footer[target_index] != None and len(footer_has_count) > 0:
                    target_number = convert_to_number(footer[target_index].replace(',',''))
                    if target_number is not None:
                        billion_number = round(target_number / 10000, 3)
                        
                        # 一般来说，都是以万为计量单位，所以募资总额至少要为亿元，小于1的不太可能
                        if 0 < billion_number < 1:
                            billion_number = target_number
                    print(f'当前计算的募资：{billion_number}亿元')
                else:
                    billion_number = -1
        except StopIteration:
            pass
        
        if billion_number < 0:
            print(footer)
            
            if len(footer_has_count) == 0 and index + 1 < len(pdf.pages):    
                billion_number = get_fund_raise_number_in_next_page(pdf.pages[index + 1])
                print('footer_has_count', billion_number)
            
            if billion_number == -1:
                
                # 直接找footer最大的数字返回，当然有的是项目总额
                # 第一遍，直接过滤出所有数字
                all_counts = [item for (index, item) in enumerate(footer) if item != None and is_number(item.replace(',',''))]
                print(all_counts)
                # 第二遍，取数逻辑
                # 数据优先级先取美制数字10,000 ；再取带小数位19.00；最后取整数
                counts = [item for (index, item) in enumerate(all_counts) if ',' in item]

                if len(counts) == 0:
                    counts = [item for (index, item) in enumerate(all_counts) if is_float(item)]
                    if len(counts) == 0:
                        counts = [item for (index, item) in enumerate(all_counts) if is_int(item)]

                if len(counts) > 0:
                    # 取数逻辑
                    counts = list(map(lambda x: convert_to_number(x.replace(',','')), counts))
                    if len(counts) > 0:
                        # 一般在最后一个数字，找最后一个数字返回
                        target_count = round(counts[-1] / 10000, 3)
                        if 1 > target_count > 0:
                            billion_number = counts[-1]
                        else:
                            billion_number = target_count
            if billion_number < -1:
                pdfparse_error_builder.create_error(PdfParserError(
                    PdfParserErrorEnum.TOTAL_FUND_NOT_IN_TABLE.value,
                    PdfParserErrorEnum.TOTAL_FUND_NOT_IN_TABLE.desc,
                    {
                        'page_number': fund_rasing_page.page_number,
                        'table': table,
                        'header': header
                    }
                ))   
    else:
        pdfparse_error_builder.create_error(PdfParserError(
            PdfParserErrorEnum.UNFIND_TOTAL_FUND_TABLE.value,
            PdfParserErrorEnum.UNFIND_TOTAL_FUND_TABLE.desc,
            {
                'page_number': fund_rasing_page.page_number
            }
        ))     
    return billion_number
         

def _parse_toc_page_number(pdf):
    toc_start_page_number = -1
    pdf_page_number_offset = 0
    toc_end_page_number = -1
    
    error_context = []

    for i in range(0, len(pdf.pages)):
        page = pdf.pages[i]
        words = page.extract_words()
        words = list(map(filter_map, words))
        
        # 先找到首字段，第一节是一定有的
        results = [word for (index, word) in enumerate(words) if len(re.findall('^第一[节|章](.*)?', word)) > 0]
        if len(results) > 0:
            toc_start_page_number = i
            pdf_page_number_offset = page.page_number - i
        
        if toc_start_page_number >=0:
            # 找尾部字段
            for word in words:
                page_number = find_number(word, -1)
                
                if page_number - pdf_page_number_offset > toc_start_page_number:
                    if toc_end_page_number > 0:
                        # print(page_number, word, toc_start_page_number, toc_end_page_number)
                        # 直接返回
                        return [toc_start_page_number, toc_end_page_number, pdf_page_number_offset]
                    toc_end_page_number = page_number - pdf_page_number_offset 
            if toc_end_page_number == -1:
                error_context.append({
                    'page_number': page.page_number,
                    'words': words
                })      

    if toc_end_page_number == -1:
        pdfparse_error_builder.create_error(PdfParserError(
            PdfParserErrorEnum.UNFIND_TOC_END_PAGE.value,
            PdfParserErrorEnum.UNFIND_TOC_END_PAGE.desc,
            {
                'context': error_context
            }
        ))       
    return [toc_start_page_number, toc_end_page_number, pdf_page_number_offset]
'''
    解析招股说明书pdf的目录（不含子小节）
'''
def parse_toc(pdf):
    [toc_start_page_number, toc_end_page_number, pdf_page_number_offset] = _parse_toc_page_number(pdf)
    if toc_start_page_number == -1:
        pdfparse_error_builder.create_error(PdfParserError(
                PdfParserErrorEnum.UNFIND_TOC_START_PAGE.value,
                PdfParserErrorEnum.UNFIND_TOC_START_PAGE.desc
            ))
    
    # 目录
    toc_list = []
    
    '''
        构建目录，
        1.检测第x节，获取开始index，
        2.检测其后面的第一个数字，获取结束index
        3.循环检测，直到没有第x节的字样
        这样就能构建出其所有的目录，
    '''
    error_context = []
    if toc_start_page_number > 0 and toc_end_page_number > 0:
        page_len = len(pdf.pages)
        # print(toc_start_page_number, toc_end_page_number)
    
        for i in range(toc_start_page_number, toc_end_page_number + 1):
            if i < page_len:
                page = pdf.pages[i]
                words = page.extract_words()
                words = list(map(filter_map, words))

                toc_indexs = [index for (index, item) in enumerate(words) if len(re.findall('^第.*[节|章](.*)?', item)) > 0]

                if len(toc_indexs) == 0:
                    pdfparse_error_builder.create_error(PdfParserError(
                        PdfParserErrorEnum.UNFIND_TOC_TOTAL_FUND_PAGE.value,
                        PdfParserErrorEnum.UNFIND_TOC_TOTAL_FUND_PAGE.desc,
                        context={
                            'toc_indexs': toc_indexs,
                            'words': words
                        }
                    ))

                # print(toc_indexs)
                for toc_index in toc_indexs:
                    toc_number_index = -1
                    # 往下走拿到第一个数字的页码
                    for index, word in enumerate(words):
                        if index >= toc_index:
                            # print('index, word',index, word)
                            number = find_number(word)
                            
                            if number is not None:
                                toc_number_index = index
                            if toc_number_index > -1:
                                break
                    
                    if toc_number_index > -1:
                        chapter = ''.join(words[toc_index:toc_number_index+1])
                        error_context.append({
                            'toc_index':toc_index,
                            'toc': chapter
                        })
                        if chapter != '':
                            # 放入目录
                            if len(re.findall(r'^(第.*[节|章]).*?(\.{2,}|\·{2,})(\d+$)',chapter)) > 0:
                                toc_list.append(chapter)

    if list(toc_list) == 0:
        pdfparse_error_builder.create_error(PdfParserError(
            PdfParserErrorEnum.UNABLE_TO_BUILD_TOC.value,
            PdfParserErrorEnum.UNABLE_TO_BUILD_TOC.desc,
            context={
                'tocs': error_context
            }
        ))
    print(toc_list, pdf_page_number_offset)
    return (toc_list, pdf_page_number_offset)


def parse_pdf(path_or_buffer):
    try:
        if isinstance(path_or_buffer, str):
            print('file_path', path_or_buffer)
            pdfparse_error_builder.set_filename(path_or_buffer)
        
        # 目录
        toc_list = []
        # pdf文件上的页码和读取到plumber中排序得到的index的差距，一般而言是1
        pdf_page_number_offset = 0

        # 募资页码    
        fund_rasing_page_number = -1
        
        # 募资金额
        billion_number = -1
        
        # 错误信息
        error_page_number = -1
        error_words = []
        
        
        with pdfplumber.open(path_or_buffer) as pdf:
            # 1.解析toc
            (toc_list, pdf_page_number_offset) = parse_toc(pdf)
            
            # 2.找募资金额所在页码 
            toc_funds_iter = (toc for toc in toc_list if toc.find('募集资金') > -1)
            toc_funds = [toc for toc in toc_list if toc.find('募集资金') > -1]
            try:
                toc_fund = next(toc_funds_iter)
                fund_rasing_page_number = re.search(r'\d+',toc_fund).group()
                fund_rasing_page_number = int(fund_rasing_page_number)
                fund_rasing_page_number -= pdf_page_number_offset
            except StopIteration:
                pdfparse_error_builder.create_error(PdfParserError(
                    PdfParserErrorEnum.UNFIND_TOC_TOTAL_FUND_PAGE.value,
                    PdfParserErrorEnum.UNFIND_TOC_TOTAL_FUND_PAGE.desc,
                    context={
                        'toc_list': toc_list
                    }
                ))
                #raise Exception('未找到募集资金运用页，退出')
                print('未找到募集资金运用页，退出')
                pass
            
            print('募集资金运用所在页码', fund_rasing_page_number)
            # 4.定位募资说明页码，解出table，并拿到第一个table的header和最后一列，
            # print('fund', fund_rasing_page_number)

            # 3.遍历前后的页码5张页找募集资金数据
            if fund_rasing_page_number > 0:
                # 因为页面内容页码和软件显示页码会有差异，找前后三个页数，找到最终表
                for i in range(fund_rasing_page_number - 2,fund_rasing_page_number + 3):
                    page = pdf.pages[i]
                    print('当前页', page)
                    current_billion_number = get_fund_raise_number(page,i, pdf)
                    if current_billion_number == None:
                        tables = page.find_tables()
                        if len(tables) > 0:
                            # 第一个table是募资资金表
                            error_words = tables[0].extract()
                        # else:
                        #     print('没有募资金额表格')
                        error_page_number = i
                    elif current_billion_number > 0:
                        billion_number = current_billion_number
                    
                    if billion_number > 0:
                        break
                    

            
            if billion_number == -1:
                pdfparse_error_builder.log_error()
                # raise Exception(f'找不到募资金额,出错页码{error_page_number},出错table:{error_words}')
                # print(f'找不到募资金额,出错页码{error_page_number},出错table:{error_words}')
            else:
                print(f' 总计募资：{billion_number}亿元')
            return billion_number
    except Exception as error:
        print('解析文件错误: ',error)        

