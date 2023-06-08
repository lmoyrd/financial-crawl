from typing import Tuple
import psycopg2
import psycopg2.extras

class PostgreConnect():
    connector = None
    cursor = None
    def __init__(self, host = 'localhost', port = 5432, dbname = 'test_ipo3', user = 'postgres') -> None:
        
        
        self.connector =  psycopg2.connect(
            """
                host=%s
                port=%s
                dbname=%s
                user=%s
            """ % (host, port, dbname, user),
            # 设置schema
            options="-csearch_path=public")
        self.connector.set_client_encoding('UTF8')
        self.cursor = self.connector.cursor(cursor_factory=psycopg2.extras.DictCursor)
    

def get_postgre_link():
    from scrapy.utils.project import get_project_settings
    
    project_settings = get_project_settings()
    database_config = project_settings.attributes['DATABASE_CONFIG'].value
    print('database_config', database_config)
    postgre_link = PostgreConnect(
        host=database_config['host'], 
        port=database_config['port'], 
        dbname=database_config['dbname'], 
        user=database_config['user']
    )
    return postgre_link



class PostgreConnector():
    connector = None
    cursor = None
    def __init__(self, postgre_link = get_postgre_link()) -> None:
        self.connector = postgre_link.connector
        self.cursor = postgre_link.cursor
    def __getitem__(self, key):
        return getattr(self, key)

    def _build_update_sql_(self, key_string, item_dict, primary_key, table) -> Tuple:
        if key_string == '' or key_string == None or item_dict == None or primary_key == '' or primary_key == None or table == '' or table == None:
            return None
        where_sql = ''
        tuple_sql = ()
        update_sql = ''
        keys = key_string.replace(' ', '').replace('\n', '').split(',')
        primary_keys = primary_key.replace(' ', '').replace('\n', '').split(',')
        keys += primary_keys
        print(keys, primary_keys)
        for key in keys:
            tuple_sql += (item_dict[key],)
            if key not in primary_keys:
                update_sql += f"{key}=(%s),"
            else:
                where_sql += f"{key}=(%s) and"
        
        result_sql = """
            UPDATE \"%s\" SET %s where %s;
        """ % (table, update_sql[:-1], where_sql[:-4])
        return [result_sql, tuple_sql]

    def _build_sql_(self, key_string, item_dict, primary_key, table) -> Tuple:
        if key_string == '' or key_string == None or item_dict == None or primary_key == '' or primary_key == None or table == '' or table == None:
            return None
        insert_sql = ''
        value_sql = ''
        tuple_sql = ()
        update_sql = ''
        keys = key_string.replace(' ', '').replace('\n', '').split(',')
        primary_keys = primary_key.replace(' ', '').replace('\n', '').split(',')
        for key in keys:
            insert_sql += f"{key},"
            value_sql += "%s,"
            tuple_sql += (item_dict[key],)
            if key not in primary_keys:
                update_sql += f"{key} = EXCLUDED.{key},"
        
        result_sql = """
            insert into \"%s\" (%s) values (%s) ON CONFLICT (%s)
            DO UPDATE SET %s ;
        """ % (table, insert_sql[:-1], value_sql[:-1], primary_key, update_sql[:-1])
        return [result_sql, tuple_sql]
    
    def _build_select_sql(self, primary_string, primary_value, table) -> Tuple:
        result_sql = 'select * from \"%s\" where %s'% (table, primary_string)
        return [f'{result_sql}=%s;', (str(primary_value), )]
    
    def execute(self, sql, value) -> None: 
        content = self.cursor.mogrify(sql, value)
        self.cursor.execute(content)
        self.commit()        

    def commit(self) -> None:
        self.connector.commit()
    
    def insert_or_update_count(self, count_dict) -> object:
        print(','.join(count_dict.keys()), count_dict)
        [result_sql, tuple_sql] = self._build_sql_(key_string=','.join(count_dict.keys()),item_dict=count_dict, primary_key='stock_exchange_desc, date, issue_market, business_type', table='MARKET_COUNT')
        self.execute(result_sql, tuple_sql)

class ZBPostgreConnector(PostgreConnector):
    def is_ipo_updated(self, project_id, update_time, update_date) -> bool:
        projects = self.get_ipo(project_id)
        existed_projects = [item for i, item in enumerate(projects) if item['update_time'] == update_time]
        is_update = len(existed_projects) == 0
        if is_update == True:
            print('existed_projects: %s 之前更新时间：%s , 现在的时间: %s' % (projects[0]['company_name'], projects[0]['update_date'], update_date))
        return is_update
         
    def is_ipo_existed(self, project_id) -> bool:
        projects = self.get_ipo(project_id)
        return len(projects) > 0
    
    def get_ipo(self, project_id) -> list:
        [result_sql, tuple_sql] = self._build_select_sql('project_id', project_id, 'ZB_IPO')
        self.execute(result_sql, tuple_sql)
        projects = self.cursor.fetchall()
        return projects

    def insert_or_update_ipo(self, project_dict) -> object:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""project_id, total_fund_rasing, stage, csrc_code, sponsor_id, sponsor_name, sponsor_code,
            company_id, update_date, create_date, company_name, stage_name, issue_market, csrc_desc,issue_market_desc,
            update_time, create_time""",item_dict=project_dict, primary_key='project_id', table='ZB_IPO')
        self.execute(result_sql, tuple_sql)
        return self.get_ipo(project_dict['project_id'])

    def get_process(self, id) -> list:
        [result_sql, tuple_sql] = self._build_select_sql('id', id, 'ZB_PROCESS')
        self.execute(result_sql, tuple_sql)
        porcesses = self.cursor.fetchall()
        return porcesses

    def insert_or_update_process(self, dict, extra_key_string = '') -> object:
        key_string = """id, project_id, company_id, company_name, stage, stage_name, timestamp, date"""
        if extra_key_string != '':
            key_string += f',{extra_key_string}'
        [result_sql, tuple_sql] = self._build_sql_(key_string=key_string,item_dict=dict, primary_key='id', table='ZB_PROCESS')
        self.execute(result_sql, tuple_sql)
        return self.get_process(dict['id'])
    
    def get_file(self, file_id) -> list:
        [result_sql, tuple_sql] = self._build_select_sql('file_id', file_id, "ZB_FILE")
        self.execute(result_sql, tuple_sql)
        files = self.cursor.fetchall()
        return files

    def insert_or_update_file(self, file_dict) -> object:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""file_id, project_id, company_id, company_name, stage, stage_name, file_name, file_url, file_type_of_process, file_type_of_audit, file_type_of_process_desc, file_type_of_audit_desc, publish_time, publish_date""",item_dict=file_dict, primary_key='file_id', table='ZB_FILE')
        self.execute(result_sql, tuple_sql)
        return self.get_file(file_dict['file_id'])