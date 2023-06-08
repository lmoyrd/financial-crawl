
# def my_func_template(func):
#     def my_func_logic(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, *args):
#         return func(originValue,  column , record, enums, target_cloumn, *args)
    
#     return my_func_logic
from pydash import get

from crawler.converter.common import time
from crawler.util.util import is_int

'''
common converter function
'''

def build_stage_status(enum_name):
    def _stage_status(originValue,  column = {}, record = {}, enums = {}, *args):
        result = None
        SH_IPO_STAGE = get(enums, f'{enum_name}.values') or {}
        retrive_key = None
        for stage_key, stage_item in SH_IPO_STAGE.items():
            value = stage_item.get('value', None)
            if value != None and originValue == value:
                status_field = stage_item.get('retriveField', None)
                if status_field != None:
                    result = record.get(status_field, None)
                    retrive_key = status_field
        
        result = result or None
        try:
            if 'targetType' in column:
                type_func = eval(column['targetType'])
                result = type_func(result)
        except Exception as error:
            # 默认行为
            # print(error)
            pass
        return result
    return _stage_status

def build_stage_status_name(enum_name, stage_status_func):
    def _stage_status_name(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, result_record = {}):
        stage = result_record.get('stage', None)
        stage_enum = enums.get(enum_name, {}).get('values', {})
        result = ''
        if stage != None:
            [stage_status_enum] = [s_status for i, s_status in stage_enum.items() if str(s_status['value']) == str(stage)] or [None]
            if stage_status_enum != None:
                stage_status_enum_values = stage_status_enum.get('status', [])
                stage_status_ = stage_status_func(stage, column, record, enums, target_cloumn)
                [result_status] = [s_status['name'] for i, s_status in enumerate(stage_status_enum_values) if str(s_status['value']) == str(stage_status_)] or ['']
                result = result_status
                
        return result
    return _stage_status_name


'''
common converter
'''
def _code(originValue, *args):
    return ''

def _csrc_parent_code(originValue, *args):
    csrc_code = _csrc_code(originValue)
    return csrc_code[0] if csrc_code != '' else ''


# ipo = dict(map(lambda func: (func.__name__, func), _ipo_set))
def _province(originValue, *args):
    result = ''
    if isinstance(originValue, list):
        [item, *others] = originValue
        result = item.get('s_province', '')
    return result

def _abbr(originValue, *args):
    result = ''
    if isinstance(originValue, list):
        [item, *others] = originValue
        result = item.get('s_issueCompanyAbbrName', '')
    return result


def _city(originValue, *args):
    result = ''
    if isinstance(originValue, list):
        [item, *others] = originValue
        result = item.get('s_areaNameDesc', '')
    return result

def _loc(originValue, *args):
    result = ''
    province = _province(originValue, args)
    city = _city(originValue, args)
    if province == '境外':
        result = province
    else:
        result = f'{province}-{city}' if province and city else ''
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

def _sponsor_id(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, *args):
    [result, *args] = _get_intermediary(originValue, column, record, enums, target_cloumn, 'SPONSOR')
    return result

def _sponsor_name(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, *args):
    [*args, result] = _get_intermediary(originValue, column, record, enums, target_cloumn, 'SPONSOR')
    return result

def _sub_sponsor_id(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, *args):
    sponsors = _get_all_intermediary(originValue, column, record, enums, target_cloumn, 'SPONSOR')
    [sub_sponsor, *args] = [sponsor for i, sponsor in enumerate(sponsors) if is_int(sponsor['i_intermediaryOrder']) and int(sponsor['i_intermediaryOrder']) > 1] or [None]
    return sub_sponsor.get('i_intermediaryId', None) if isinstance(sub_sponsor, dict) else None

def _sub_sponsor_name(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, *args):
    sponsors = _get_all_intermediary(originValue, column, record, enums, target_cloumn, 'SPONSOR')
    [sub_sponsor, *args] = [sponsor for i, sponsor in enumerate(sponsors) if is_int(sponsor['i_intermediaryOrder']) and int(sponsor['i_intermediaryOrder']) > 1] or [None]
    return sub_sponsor.get('i_intermediaryName', '') if isinstance(sub_sponsor, dict) else ''



def _law_office_id(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, *args):
    [result, *args] = _get_intermediary(originValue, column, record, enums, target_cloumn, 'LAW_FIRM')
    return result

def _law_office_name(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, *args):
    [*args, result] = _get_intermediary(originValue, column, record, enums, target_cloumn, 'LAW_FIRM')
    return result


def _accounting_firm_id(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, *args):
    [result, *args] = _get_intermediary(originValue, column, record, enums, target_cloumn, 'ACCOUNTING_FIRM')
    return result

def _accounting_firm_name(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, *args):
    [*args, result] = _get_intermediary(originValue, column, record, enums, target_cloumn, 'ACCOUNTING_FIRM')
    return result

def _rating_agency_id(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, *args):
    [result, *args] = _get_intermediary(originValue, column, record, enums, target_cloumn, 'RATING_AGENCY')
    return result

def _rating_agency_name(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, *args):
    [*args, result] = _get_intermediary(originValue, column, record, enums, target_cloumn, 'RATING_AGENCY')
    return result

def _asset_evaluation_institute_id(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, *args):
    [result, *args] = _get_intermediary(originValue, column, record, enums, target_cloumn, 'ASSET_EVALUATION_INSTITUTE')
    return result

def _asset_evaluation_institute_name(originValue,  column = {}, record = {}, enums = {}, target_cloumn = {}, *args):
    [*args, result] = _get_intermediary(originValue, column, record, enums, target_cloumn, 'ASSET_EVALUATION_INSTITUTE')
    return result





def _file_url(originValue, *args):
    return "http://kcb.sse.com.cn%s" % (originValue) if originValue != '' else ''


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

def _person_name(originValue,  *args):
    # 名字中会存在 '（已离职）' 或 '(已离职)' 这两种形式
    return (originValue or '').replace('(已离职)', '').replace('（已离职）', '')

def _resignation(originValue,  *args):
    return '离职' if '（已离职）' in (originValue or '') else ''





base_project = {
    'csrc_code': _csrc_code,
    'csrc_desc': _csrc_desc,
    'law_office_id': _law_office_id,
    'law_office_name': _law_office_name,
    'sponsor_id': _sponsor_id,
    'sponsor_name': _sponsor_name,
    'sub_sponsor_id': _sub_sponsor_id,
    'sub_sponsor_name': _sub_sponsor_name,
    'accounting_firm_id': _accounting_firm_id,
    'accounting_firm_name': _accounting_firm_name,
    'rating_agency_id': _rating_agency_id,
    'rating_agency_name': _rating_agency_name,
    'asset_evaluation_institute_id': _asset_evaluation_institute_id,
    'asset_evaluation_institute_name': _asset_evaluation_institute_name,
    'update_time': time(),
    'create_time': time(),
    'accept_apply_time': time(),
}

# 上交所company的converter
company = {
    "province": _province,
    "abbr": _abbr,
    "city": _city,
    "loc": _loc
}
# 上交所intermediary的converter
intermediary = {

}
# 用于把intermediate转化成company的converter
intermediary_company = {

}

# 上交所company_manager的converter
company_manager = {

}
# 上交所person的converter


person = {
    'name': _person_name
}

sh_intermediary_person = {
    'name': _person_name,
    'resignation': _resignation
}

sh_intermediary = {

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
}


file = {
    "publish_time": time(),
    "file_url": _file_url,
    "file_version_desc": _file_version_desc,
}

