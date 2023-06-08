# -*- coding: utf-8 -*-

import json
import time
import os
import datetime
import re
import attrs
import types
from pydash import objects

def delete_all_records():
    from crawler.util.postgre import get_postgre_link
    db_link = get_postgre_link()
    connector = db_link.connector
    cursor = db_link.cursor
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    table_names = cursor.fetchall()

    # 清除所有表中的记录
    for table in table_names:
        cursor.execute("DELETE FROM \"{}\" WHERE true".format(f'{table[0]}'))

    # 提交更改并关闭游标和连接
    connector.commit()
    cursor.close()
    connector.close()
    print('delete success')

def get_current_time(): 
    current_milli_time = lambda: int(round(time.time() * 1000))
    return current_milli_time()

def get_time_str(milli_time, format_str = '%Y-%m-%d %H:%M:%S'):
    return time.strftime(format_str,time.localtime(milli_time/1000)) 

def get_today_str(*strs):
    current_milli_time = get_current_time()
    today_str = get_time_str(current_milli_time, '%Y-%m-%d')
    return today_str

def create_today_folder(root_path):
    # 代码执行根目录是从运行目录开始，scrapy文件目录结构是 projectname/projectname/spiders,spider存放了所有的爬虫，scrapy运行的目录结构是projectname/projectname
    # 所以这里的文件路径计算规则只要在往上一层即可
    
    target_root_path= os.path.join(os.path.abspath(os.path.join(root_path, "..")), 'data')
    
    root_path_existed = os.path.exists(target_root_path)

    if not root_path_existed:
        os.makedirs(target_root_path)
    today_path = os.path.join(target_root_path, get_today_str())
    today_path_existed = os.path.exists(today_path)
    if not today_path_existed:
        os.makedirs(today_path)
    return today_path
    
def get_crawl_file_prefix(root_path):
    now = datetime.datetime.now()
    today_path = create_today_folder(root_path)
    filename_prefix = now.strftime('%Y-%m-%d %H-%M-%S')
    
    return os.path.join(today_path, filename_prefix)

def get_date_obj(time_str, format = '') -> datetime.datetime:
    date_obj = None
    formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%d %H:%M']
    if format != '' and format != None:
        formats.insert(0, format)
    
    for format in formats:
        if date_obj != None:
            break
        else:
            try:
                date_obj = datetime.datetime.strptime(time_str, format)
            except:
                pass
    return date_obj
   
def convert_time(time_str):
    date_obj = get_date_obj(time_str)
    return int(round(date_obj.timestamp() * 1000)) if date_obj != None else ''

def get_time_in_array(time_str, format = '%H:%M'):
    date_obj = get_date_obj(time_str, format)
    return [date_obj.hour, date_obj.minute] if date_obj != None else [-1, -1]

current_crawl = ''
def set_crawl(crawl_name):
    global current_crawl
    current_crawl = crawl_name
    return current_crawl

def get_crawl():
    global current_crawl
    return current_crawl



def to_dict(self):
    """
    默认导出的dict携带property标记的属性
    """
    dic = attrs.asdict(
        self,
        # 只能按约定_打头是private属性，更好的是decorator
        filter=lambda attr, value: not attr.name.startswith("_")
    )
    
    dic.update({n: p.__get__(self) for n, p in vars(type(self)).items() if isinstance(p, property)})
    return dic

def get_source_map(self):
    """
    获取与api返回的数据结构的映射关系
    """
    source_dict = {}
    for field in attrs.fields(type(self)):
        if field.metadata.get('source'):
            source_dict[field.name] = field.metadata['source']
    return source_dict


def load_item(self, retrive_dict = {}):
    """
    用于执行api数据到标准数据结构的映射
    """
    fields = attrs.fields(type(self))
    source_dict = self.get_source_map()
    for key, value in source_dict.items():
        field = [field for i, field in enumerate(fields) if field.name == key]
        if len(field) > 0:
            field = field[0]
        else:
            field = None
        default_value = field.default if field != None else ''
        # 支持函数
        if isinstance(value, types.FunctionType):
            result = value(self, retrive_dict)
        # 支持自定义格式，格式为 path#{rule: condition=condition_value, path: path}#...这样一级一级往下去
        elif re.search( r'\{.*\}', value):
            paths = value.split('#')
            result = retrive_dict
            for path in paths:
                if result == '':
                    break
                try:
                    rule_object = json.loads(path)
                except:
                    rule_object = None
                if rule_object:
                    target_path = None
                    if len(rule_object.values()) == 2:
                        rule, target_path = rule_object.values()
                    else:
                        rule, *other = rule_object.values()
                    rule_path, rule_value = rule.split('=')
                    if type(result) == list:
                        intermediary_list = [item for i, item in enumerate(result) if str(item[rule_path]) == rule_value]
                        if len(intermediary_list) > 0:
                            [intermediary, *other] = intermediary_list
                            if target_path != None:
                                result = intermediary[target_path]
                            else:
                                result = intermediary
                        else:
                            result = default_value
                    elif type(result) == dict:
                        if str(result[rule_path]) == rule_value:
                            result = result[target_path] if target_path in result.keys() else ''
                        else:
                            result = default_value
                    else:
                        result = default_value
                else:
                    try:
                        result = objects.get(retrive_dict,path)
                    except:
                        result = default_value
            #retrive_dict[path]
        elif re.search( r'\|', value):
            paths = value.split('|')
            result = None
            for path in paths:
                if result != None:
                    break
                try:
                    result = objects.get(retrive_dict,path)
                except:
                    result = default_value
        else:
            result = objects.get(retrive_dict,value)
        setattr(self, key, result if result != None else None)
    return self.to_dict()

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


def convert_to_int(value):
    """
    转换成int
    """
    result
    try:
        result = int(value)
    except:
        result = None
    return result