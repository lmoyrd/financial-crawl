import json
import re
from os import path
from pydash import merge, clone_deep, merge_with

from crawler.util.util import delete_all_records
from crawler.util.postgre import get_postgre_link


def customizer(obj_value, src_value, key, obj, source):
    if isinstance(obj_value, list) and isinstance(src_value, list):
        # 这样就实现自ipo -> sh -> common的覆盖，任一层都可以任意写column，最终最低层如果存在同名targetName，会直接覆盖
        if key == 'columns':
            merged = obj_value.copy()
            for item in src_value:
                [target] = [t_target for t_target in obj_value if t_target['targetName'] == item['targetName']] or [None]
                if target == None:
                    merged.append(item)
            return merged
        else:    
            # 将两个字典数组合并到一个列表中
            merged_list = obj_value + src_value

            # 将列表转换成集合类型，并取并集
            result_set = set(frozenset(d.items()) for d in merged_list)

            # 将结果转换回字典数组类型
            result_dict_list = [dict(s) for s in result_set]
            return result_dict_list
    return None


class TableLoader: 
    db_json = {}
    tables = {} # key为scope，如sh_ipo
    def __init__(self, parent_dir, delete_all = False) -> None:
        self.db_json = self.load_db_json(parent_dir)
        self.generate_tables()
        if delete_all:
            delete_all_records()
    
    def load_db_json(self, parent_dir):
        # 读取 JSONC 文件内容
        
        with open(path.join(parent_dir, 'db.jsonc'), 'r') as f:
            content = f.read()

        # 去除注释
        content = re.sub(r'\/\/.*\n', '', content)

        # 加载 JSON 格式数据
        data = json.loads(content)

        db_json = json.dumps(data, indent=4)

        data = json.loads(db_json)
        return data
    
    def generate_tables(self):
        root_common_enums = {}
        root_common_tables = {}
        scope_common_enums = {}
        scope_common_tables = {}
        special_field_table = "a_tables"
        special_field_enums = "enums"
        special_field_fields = "fields"
        for field_key, value in self.db_json.items():
            if field_key == special_field_table:
                root_common_tables = value
            elif field_key == special_field_enums:
                root_common_enums = value
            else:
                # 下钻到scope这一层
                if isinstance(value, dict):
                    for parent_scope_name, scope in value.items():
                        # 下钻到sh这一层
                        if isinstance(scope, dict):
                            for scope_field_key, scope_field_value in scope.items():
                                if scope_field_key == special_field_table:
                                    scope_common_tables = scope_field_value
                                elif scope_field_key == special_field_enums:
                                    scope_common_enums = scope_field_value
                                elif scope_field_key == special_field_fields:
                                    pass
                                else:
                                    # 下钻到ipo这一层
                                    if isinstance(scope_field_value, dict):
                                        self.tables[f'{parent_scope_name}_{scope_field_key}'] = {}
                                        tables = {}
                                        enums = {}
                                        target_tables = {}
                                        for target_field_key, target_field_value in scope_field_value.items():
                                            if target_field_key == special_field_table:
                                                # print('root_common_tables', root_common_tables)
                                                # print('scope_common_tables', scope_common_tables)
                                                # print('target_field_value', target_field_value)
                                                # 传递多个的src的时候，前后相邻的AB，在customizer中A是obj，B是src，所以才一致不对
                                                tables = merge_with({}, target_field_value, scope_common_tables, root_common_tables , customizer)
                                                # print('table1', root_common_tables)
                                                # print('table2', scope_common_tables)
                                                # print('table3', target_field_value)
                                                # print('tables', tables)
                                            elif target_field_key == special_field_enums:
                                                # 由root、scope、及各crawler对应的层的enmus合并而成
                                                enums = merge_with(enums, root_common_enums, scope_common_enums, target_field_value, customizer)
                                                
                                            else:
                                                target_tables = target_field_value
                                        
                                        tables = merge_with(tables, target_tables, customizer)
                                        

                                        # 与Common Table去重，并创建Tables
                                        # 下钻到tables这一层（各crawler对应的层）
                                        for target_table_name, target_table in tables.items():
                                            # print('table', target_table_name, target_table)
                                            columns = target_table.get('columns', [])
                                            columns_copy = clone_deep(columns)
                                            for column in columns_copy:
                                                if 'targetType' not in column:
                                                    column['targetType'] = column['originType']
                                                if 'converterType' in column and column['converterType'] == 'type' and column['converter'] != '':
                                                    column['targetType'] = column['converter']
                                            table = Table(target_table_name, enums, columns_copy)
                                            self.tables[f'{parent_scope_name}_{scope_field_key}'][target_table_name] = table
                                            # 收集成功了


    def load_table(self, scope, table_name):
        if self.tables[scope] != None and table_name != None and self.tables[scope][table_name.upper()] != None:
            return self.tables[scope][table_name.upper()]
        return None

# converter如何调用？
class Table: 
    enums = {}
    columns = [] # Column[]
    records = []
    name = ''

    # 此部分属性需要在真正使用化时传入
    db_link = get_postgre_link()
    cursor = db_link.cursor
    connector = db_link.connector
    converters = {} # table的字段converter都存放在此

    def __init__(self, name, enmus, columns):
        self.name = name
        self.columns = clone_deep(columns)
        self.enums = enmus
        self.items = []
        self.records = []
        # 要命名成私有(带下划线)才可以，否则是一个引用
        self._target_columns = []
    
    # def bind_converters(self, converter):
    #     self.converters = converter

    def load_records(self, records = []):
        for record in records:
            self.load_record(record, False)
    
    def load_record(self, record, debug = False):
        if record not in self.records:
            # print(self.name, record)
            self.records.append(record)
            [_target_columns, _cur_result_record] = self._build_record(record, debug)
            if _target_columns not in self.items:
                self.items.append(_target_columns)
            return [_target_columns, _cur_result_record]
        return [[], {}]
    
    def _build_record(self, record, debug = False):
        self._cur_result_record = {}
        self._target_columns = []
        for column in self.columns:
            target_cloumn = clone_deep(column)
            originName = column.get('originName', '')
            
            # 默认值，针对不同类型设置不同的默认值
            defaultValue = column.get('defaultValue', None)
            
            # originValue = record.get(originName) if originName != '' else defaultValue
            # 还是妥协了
            for oValue in originName.split('|'):
                originValue = record.get(oValue, '') if oValue != '' else defaultValue
                if originValue != '':
                    pass
            
            # 只允许多一个来源字段，当然可以扩展，但无限扩展还是算了
            subOriginName = column.get('subOriginName', '')
            
            if subOriginName != '' and originValue == '':
                originValue = record.get(subOriginName, '') if subOriginName != '' else ''
            # target_cloumn['originValue'] = originValue
            targetName = column.get('targetName', '')
            comment = column.get('comment', '')
            converterType = column.get('converterType', '')
            
            if converterType == 'type':
                converter = column.get('converter', 'string')
                converter_func = eval(converter)
                
                try:
                    value = converter_func(originValue)
                    # if targetName == 'sub_biz_type':
                    #     print('sub_biz_type:', originName, targetName, originValue, value)
                    target_cloumn['targetValue'] = value
                except Exception as e:
                    target_cloumn['targetValue'] = defaultValue
                    # print(self.name, column, originValue, e)
            elif converterType == 'enum':
                enum_name = column.get('converter', originName)
                enum = self.enums.get(enum_name , None)
                enum_path = column.get('enumPath', '')
                
                if enum != None:
                    values = enum.get('values', {})
                    if isinstance(values, dict):
                        if enum_path != '':
                            paths = enum_path.split('.')
                            curr_path_values = values
                            # 下钻获取
                            for path in paths:
                                if curr_path_values != None and isinstance(curr_path_values, dict):
                                    curr_path_values = curr_path_values.get(path, None)
                            target_cloumn['targetValue'] = curr_path_values or ''
                        else:
                            for key, value_obj in values.items():
                                value = value_obj['value']
                                # 取出value值与record中原始值相同的数据
                                if str(value) == str(originValue):
                                        target_cloumn['targetValue'] = value_obj['desc'] or ''
                    else:
                        target_cloumn['targetValue'] = originValue
                else:
                    target_cloumn['targetValue'] = originValue
            elif converterType == 'function':
                converter_name = column.get('converter', targetName)
                converter = self.converters.get(converter_name , None)
                # print(converter_name, converter)
                if callable(converter):
                    target_cloumn['targetValue'] = converter(originValue, column, record, self.enums, target_cloumn, self._cur_result_record)
                else:
                    target_cloumn['targetValue'] = originValue
            else:
                target_cloumn['targetValue'] = originValue

            if target_cloumn.get('targetValue') == None:
                target_cloumn['targetValue'] = defaultValue

            self._cur_result_record[targetName] = target_cloumn.get('targetValue') or defaultValue
            self._target_columns.append(target_cloumn)
        
        output = json.dumps(self._target_columns, ensure_ascii=False, indent=4)
        if debug == True:
            print('debug', debug)
            print(self.name, output.encode('utf-8').decode('utf-8'))
        return [clone_deep(self._target_columns), clone_deep(self._cur_result_record)]

    def is_updated(self, record, update_keys = []): 
        [_target_columns, _cur_result_record] = self._build_record(record)
        items = self.get_items(_target_columns) or [None]
        if len(items) == 0:
            return True
        else:
            # print(dict(items[0]), update_keys, _cur_result_record)
            result = [(lambda item, update_key: update_key in item and update_key in _cur_result_record and item[update_key] == _cur_result_record[update_key])(item, update_key) for i, item in enumerate(items) for update_key in update_keys]
            # print(result)
            false_list = list(filter(lambda x: x is False, result))
            return len(false_list) > 0

    def is_exist(self, record):
        [_target_columns, _cur_result_record] = self._build_record(record)
        return len(self.get_items(_target_columns)) > 0

    def get_items(self, target_columns):
        [result_sql, tuple_sql] = self._build_select_sql(target_columns)
        if result_sql != None:
            self._execute_(result_sql, tuple_sql)
            results = self.cursor.fetchall()
            return results
        return []

    def create_table(self):
        # 后续补充
        pass
    
    def clear(self):
        self.records = []
        self.items = []
        return None

    def save(self):
        for item in self.items:
            self.save_item(item)
        self.items = []
        return None
    
    def save_item(self, item):
        # 先尝试写入，在尝试更新
        [result_sql, tuple_sql] = self._build_item_update_sql_(item)
        self._execute_(result_sql, tuple_sql)
        return None

    
    def _execute_(self, sql, value) -> None: 
        
        content = self.cursor.mogrify(sql, value)
        # print('sql', sql)
        # print('value', value)
        # print('content', content)
       
        self.cursor.execute(content)
        self.connector.commit()

    def _build_select_sql(self, item):
        primary_value = None
        primary_string = ''
        result_sql = ''
        for column in item:
            if isinstance(column, dict):
                key = column.get('targetName', '')
                is_primary = bool(column.get('primaryKey', False))
                primary_value = column.get('targetValue', None)
                if key != '' and is_primary == True and primary_value != None:
                    primary_string = key
                    break
        if primary_string != '' and primary_value != None:
            result_sql = 'select * from \"%s\" where %s'% (self.name, primary_string)
        else:
            result_sql = ''
        return [f'{result_sql}=%s;', (str(primary_value), )] if result_sql != '' else [None, None]

    def _build_item_update_sql_(self, item):
        insert_sql = ''
        value_sql = ''
        tuple_sql = ()
        update_sql = ''
        primary_key = ''
        for column in item:
            
            if isinstance(column, dict):
                key = column.get('targetName', '')
                need_save = column.get('saveToDB', True)
                if need_save == False:
                    continue
                is_primary = bool(column.get('primaryKey', False))
                if key != '':
                    insert_sql += f"{key},"
                    value_sql += "%s,"
                    tuple_sql += (column.get('targetValue'),)
                    if is_primary == False:
                        update_sql += f"{key} = EXCLUDED.{key},"
                    else:
                        primary_key += f"{key},"
        # 一定要有主键
        result_sql = """
            insert into \"%s\" (%s) values (%s) ON CONFLICT (%s)
            DO UPDATE SET %s ;
        """ % (self.name, insert_sql[:-1], value_sql[:-1], primary_key[:-1], update_sql[:-1])
        
        return [result_sql, tuple_sql]
    


# sh_ipo = TableLoader(scope = 'sh_ipo', table_name = 'sh_ipo', db_connector = postgresl_db_connector)
# sh_ipo.load_record(record = record)
# sh_ipo.load_records(records = records)
# yield sh_ipo

# if not sh_ipo.exists():
#     sh_ipo.save()

# sh_ipo.save_records() => if not sh_ipo.exist_record(): sh_ipo.save_record()
