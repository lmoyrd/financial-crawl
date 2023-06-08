
# def my_func_template(func):
#     def my_func_logic(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, *args):
#         return func(originValue,  column , record, enums, target_cloumn, *args)
    
#     return my_func_logic
from pydash import get

from crawler.util.util import is_int
from crawler.converter.common import time

'''
common converter function
'''




def build_stage_status_name(enum_name):
    def _stage_status_name(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, result_record = {}):
        stage = result_record.get('stage', None)
        stage_enum = enums.get(enum_name, {}).get('values', {})
        result = ''
        if stage != None:
            [stage_status_enum] = [s_status for i, s_status in stage_enum.items() if str(s_status['value']) == str(stage)] or [None]
            if stage_status_enum != None:
                stage_status_enum_values = stage_status_enum.get('status', [])
                stage_status_ = originValue
                [result_status] = [s_status['name'] for i, s_status in enumerate(stage_status_enum_values) if str(s_status['value']) == str(stage_status_)] or ['']
                result = result_status
                
        return result
    return _stage_status_name


def build_process_stage(enum_name):
    def _process_stage(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, result_record = {}):
        # 从stage_status反推stage
        stage_status = originValue
        stage_enum = enums.get(enum_name, {}).get('values', {})
        if stage_status != None:
            for i, stage_status_enum in stage_enum.items():
                stage_status_enum_values = stage_status_enum.get('status', [])
                [result_status] = [s_status['name'] for i, s_status in enumerate(stage_status_enum_values) if str(s_status['value']) == str(stage_status)] or [None]
                if result_status != None:
                    return stage_status_enum.get('value', None)
        return None
    return _process_stage

def build_process_stage_name(enum_name):
    def _process_stage_name(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, result_record = {}):
        # 从stage_status反推stage
        stage = result_record.get('stage', None)
        stage_enum = enums.get(enum_name, {}).get('values', {})
        if stage != None:
            [result_status] = [s_status['desc'] for i, s_status in stage_enum.items() if str(s_status['value']) == str(stage)] or ['']
            return result_status
        return ''
    return _process_stage_name

def build_process_stage_status_name(enum_name):
    def _process_stage_status_name(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, result_record = {}): 
        stage_status = result_record.get('stage_status', None)
        stage_enum = enums.get(enum_name, {}).get('values', {})
        
        if stage_status != None:
            for i, stage_status_enum in stage_enum.items():
                stage_status_enum_values = stage_status_enum.get('status', [])
                [result_status] = [s_status['name'] for i, s_status in enumerate(stage_status_enum_values) if str(s_status['value']) == str(stage_status)] or [None]
                if result_status != None:
                    return result_status
        return originValue or ''
    return _process_stage_status_name

'''
common converter
'''
def _code(originValue, *args):
    return ''

def _csrc_parent_code(originValue, *args):
    csrc_code = _csrc_code(originValue)
    return csrc_code[0] if csrc_code != '' else ''


# ipo = dict(map(lambda func: (func.__name__, func), _ipo_set))


def _loc(*args):
    cur_result_record = args[-1]
    result = ''
    province = cur_result_record.get('province', '')
    city = cur_result_record.get('city', '')
    if province == '境外':
        result = province
    else:
        if province !='' and city != '':
            result = f'{province}-{city}'
        elif province !='' or city != '':
            result = province or city
        else:
            result = ''
    return result

def _csrc_code(originValue, *args):
    result = ''
    if isinstance(originValue, list):
        [item, *others] = originValue
        result = item.get('s_csrcCode', '')
    return result

def _csrc_desc(originValue, *args):
    result = ''
    if isinstance(originValue, list):
        [item, *others] = originValue
        result = item.get('s_csrcCodeDesc', '')
    return result

def _get_all_intermediary(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, intermediary_enum_name = 'LAW_FIRM'):
    result = [None]
    intermediary_type = enums.get('INTERMEDIARY_TYPE', {}).get('values', {})
    if isinstance(originValue, list):
        intermediary = [intermediary for i, intermediary in enumerate(originValue) if str(intermediary['i_intermediaryType']) == str(intermediary_type[intermediary_enum_name]['value'])] or [None]
        return intermediary
    return result

def _get_intermediary(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, intermediary_enum_name = 'LAW_FIRM'):
    result = [None, '']
    [intermediary, *args] = _get_all_intermediary(originValue, column, record, enums, target_cloumn, intermediary_enum_name)
    if intermediary != None: 
        result = [intermediary.get('i_intermediaryId', None), intermediary.get('i_intermediaryName', None)]
    return result


def _file_url(originValue, *args):
    # return "https://reportdocs.szse.cn%s" % (originValue) if originValue != None and originValue != '' else ''
    return "https://reportdocs.static.szse.cn%s" % (originValue) if originValue != None and originValue != '' else ''
    


def _file_name(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, result_record = {}):
    _file_ext = record.get('dfext', '')
    if _file_ext:
        if _file_ext in originValue:
            return originValue
        else:
            return "%s.%s" % (originValue, _file_ext)
    else:
        return "%s.pdf" % (originValue) if ".pdf" not in originValue else originValue

def _file_version_desc(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, result_record = {}):
    
    file_version_enum = get(enums, 'FILE_VERSION.values')
    file_type_enum = get(enums, 'FILE_TYPE.values')
    
    current_file_type = get(record, 'fileType')
    parse_file_version = False
    result = ''
    # print('file_type_enum', current_file_type, '-----',file_type_enum)
    if isinstance(file_type_enum, dict) and current_file_type != None:
        for key, value_obj in file_type_enum.items():
            value = value_obj['value']
            # 取出value值与record中原始值相同的数据
            if str(value) == str(current_file_type):
                parse_file_version = value_obj.get('parseFileVersion', False)
                break
        if parse_file_version == True:
            for key, version_obj in file_version_enum.items():
                value = version_obj['value']
                if str(value) == str(originValue):
                    result = version_obj.get('desc', '')
                    break
    return result

def _process_id(originValue,  column = {}, record = {}, *args):
    project_id = record.get('prjid', '')
    company_id = record.get('entid', '')
    return "%s-%s" %(project_id, company_id)

def _person_name(originValue,  *args):
    # 名字中会存在 '（已离职）' 或 '(已离职)' 这两种形式
    return (originValue or '').replace('(已离职)', '').replace('（已离职）', '')

def _resignation(originValue,  *args):
    return '离职' if '（已离职）' in (originValue or '') else ''


base_project = {
    'csrc_code': _csrc_code,
    'csrc_desc': _csrc_desc,
    'update_time': time(),
    'create_time': time(),
    'accept_apply_time': time(),
}

# 上交所company的converter
company = {
    "loc": _loc
}
# 上交所intermediary的converter
intermediary = {

}
# 用于把intermediate转化成company的converter
intermediary_company = {
    "loc": _loc
}

# 上交所company_manager的converter
company_manager = {

}
# 上交所person的converter

person = {
    'name': _person_name,
    'id': _person_name,
}

sz_intermediary_person = {
    'name': _person_name,
    'id': _person_name,
    'resignation': _resignation
}

sz_intermediary = {
    "loc": _loc
}
zjh_company = {
    'csrc_code': _csrc_code,
    'csrc_desc': _csrc_desc,
    'csrc_parent_code': _csrc_parent_code,
    'code': _code
}

intermediary = {
    'csrc_code': _csrc_code,
    'csrc_desc': _csrc_desc,
    'csrc_parent_code': _csrc_parent_code,
    'code': _code
}

process = {
    'time': time(),
    'id': _process_id
}


file = {
    "publish_time": time(),
    "file_url": _file_url,
    "file_name": _file_name,
    "file_version_desc": _file_version_desc,
}
