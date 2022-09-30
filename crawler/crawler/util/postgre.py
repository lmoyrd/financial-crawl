from typing import Tuple
import psycopg2
import psycopg2.extras

class PostgreConnect():
    connector = None
    cursor = None
    def __init__(self, host = 'localhost', port = 5432, dbname = 'postgres', user = 'postgres') -> None:
        
        
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
        [result_sql, tuple_sql] = self._build_sql_(key_string="""time, date, stock_exchange_type, stock_exchange_type_desc, count""",item_dict=count_dict, primary_key='stock_exchange_type, time', table='MARKET_COUNT')
        self.execute(result_sql, tuple_sql)


class KCBPostgreConnector(PostgreConnector):
    
    def is_company_existed(self, company_id) -> bool:
        companys = self.get_company(company_id)
        return len(companys) > 0
    
    def get_company(self, company_id) -> bool:
        if company_id == '' or company_id == None:
            return False
        # TODO: 这里可以进一步抽象 
        [result_sql, tuple_sql] = self._build_select_sql('id', company_id, 'COMPANY')
        self.execute(result_sql, tuple_sql)
        companys = self.cursor.fetchall()
        return companys

    def insert_or_update_company(self, company_dict) -> list:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""
            id, name, abbr, csrc_company_type, csrc_code, csrc_desc, province, city, csrc_parent_code, loc
        """,item_dict=company_dict, primary_key='id', table='COMPANY')
        content = self.cursor.mogrify(result_sql, tuple_sql)
        self.execute(result_sql, tuple_sql)
        return self.get_company(company_dict['id'])

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
        [result_sql, tuple_sql] = self._build_select_sql('project_id', project_id, 'KCB_IPO')
        self.execute(result_sql, tuple_sql)
        projects = self.cursor.fetchall()
        return projects

    def insert_or_update_ipo(self, project_dict) -> object:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""project_id, total_fund_rasing, stage, stage_status, biz_type, csrc_code, law_office_id, sponsor_id, sponsor_name, accounting_firm_id,
                accounting_firm_name,rating_agency_id, rating_agency_name, accept_apply_date, law_office_name, asset_evaluation_institute_id, asset_evaluation_institute_name,
                company_id, update_date, create_date, company_name, stage_name, stage_status_name, issue_market, csrc_desc,
                accept_apply_time, update_time, create_time""",item_dict=project_dict, primary_key='project_id', table='KCB_IPO')
        self.execute(result_sql, tuple_sql)
        return self.get_ipo(project_dict['project_id'])

    def __get_process__(self, id, table) -> list:
        [result_sql, tuple_sql] = self._build_select_sql('id', id, table)
        self.execute(result_sql, tuple_sql)
        porcesses = self.cursor.fetchall()
        return porcesses

    def __insert_or_update_process__(self, dict, table, extra_key_string = '') -> object:
        key_string = """id, project_id, company_id, company_name, stage, stage_name, stage_status, stage_status_name, timestamp, date"""
        if extra_key_string != '':
            key_string += f',{extra_key_string}'
        [result_sql, tuple_sql] = self._build_sql_(key_string=key_string,item_dict=dict, primary_key='id', table=table)
        self.execute(result_sql, tuple_sql)
        return self.__get_process__(dict['id'], table)
    
    def get_milestone(self, milestone_id) -> list:
        return self.__get_process__(id=milestone_id, table='KCB_MILESTONE')

    def insert_or_update_milestone(self, milestone_dict) -> object:
        return self.__insert_or_update_process__(dict=milestone_dict, table='KCB_MILESTONE')

    def get_process(self, process_id) -> list:
        return self.__get_process__(id=process_id, table='KCB_PROCESS')

    def insert_or_update_process(self, process_dict) -> object:
        return self.__insert_or_update_process__(dict=process_dict, table='KCB_PROCESS', extra_key_string='reason')
    
    def get_other(self, other_id) -> list:
        return self.__get_process__(id=other_id, table='KCB_OTHER')

    def insert_or_update_other(self, other_dict) -> object:
        return self.__insert_or_update_process__(dict=other_dict, table='KCB_OTHER', extra_key_string='reason')

    def get_file(self, file_id) -> list:
        [result_sql, tuple_sql] = self._build_select_sql('file_id', file_id, "KCB_FILE")
        self.execute(result_sql, tuple_sql)
        files = self.cursor.fetchall()
        return files

    def insert_or_update_file(self, file_dict) -> object:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""file_id, project_id, company_id, company_name, stage, stage_name, file_name, file_url, file_size, file_type_of_process, file_type_of_audit, file_type_of_process_desc, file_type_of_audit_desc, publish_time, publish_date""",item_dict=file_dict, primary_key='file_id', table='KCB_FILE')
        self.execute(result_sql, tuple_sql)
        return self.get_file(file_dict['file_id'])

    def get_intermediary(self, intermediary_id) -> list:
        [result_sql, tuple_sql] = self._build_select_sql('id', intermediary_id, "INTERMEDIARY")
        self.execute(result_sql, tuple_sql)
        intermediarys = self.cursor.fetchall()
        return intermediarys

    def insert_or_update_intermediary(self, intermediary_dict) -> object:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""id, name, abbr, csrc_company_type, csrc_code, csrc_desc, province, city, csrc_parent_code, loc""",item_dict=intermediary_dict, primary_key='id', table='INTERMEDIARY')
        self.execute(result_sql, tuple_sql)
        return self.get_intermediary(intermediary_dict['id'])

    def get_company_manager(self, manager_id) -> list:
        [result_sql, tuple_sql] = self._build_select_sql('id', manager_id, "COMPANY_MANAGER")
        self.execute(result_sql, tuple_sql)
        files = self.cursor.fetchall()
        return files

    def insert_or_update_company_manager(self, manager_dict) -> object:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""id,name, company_id, company_name, job_title""",item_dict=manager_dict, primary_key='id', table='COMPANY_MANAGER')
        self.execute(result_sql, tuple_sql)
        return self.get_company_manager(manager_dict['id'])
    
    def get_intermediary_item(self, project_id, intermediary_id) -> list:
        content = self.cursor.mogrify("""
        select * from \"KCB_INTERMEDIARY\" where project_id = %s and intermediary_id = %s;
        """, (project_id, intermediary_id, ),)
        self.cursor.execute(content)
        self.commit()
        files = self.cursor.fetchall()
        return files

    def insert_or_update_intermediary_item(self, item_dict) -> object:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""project_id, intermediary_id, type, name, intermediary_order""",item_dict=item_dict, primary_key='project_id, intermediary_id', table='KCB_INTERMEDIARY')
        self.execute(result_sql, tuple_sql)
        return self.get_intermediary_item(item_dict['project_id'], item_dict['intermediary_id'])
    
    def get_person_item(self, person_id) -> list:
        [result_sql, tuple_sql] = self._build_select_sql('id', person_id, "KCB_INTERMEDIARY_PERSON")
        self.execute(result_sql, tuple_sql)
        files = self.cursor.fetchall()
        return files

    def insert_or_update_person_item(self, person_dict) -> object:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""project_id, intermediary_id, id, name, job_type, job_title""",item_dict=person_dict, primary_key='id', table='KCB_INTERMEDIARY_PERSON')
        self.execute(result_sql, tuple_sql)
        return self.get_person_item(person_dict['id'])


class CYBPostgreConnector(PostgreConnector):
    def is_company_existed(self, company_id) -> bool:
        companys = self.get_company(company_id)
        return len(companys) > 0
    
    def get_company(self, company_id) -> bool:
        if company_id == '' or company_id == None:
            return False
        [result_sql, tuple_sql] = self._build_select_sql('id', company_id, 'CYB_COMPANY')
        self.execute(result_sql, tuple_sql)
        companys = self.cursor.fetchall()
        return companys

    def insert_or_update_company(self, company_dict) -> list:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""
            id, name, abbr, csrc_company_type, csrc_code, csrc_desc, province, city, csrc_parent_code, loc
        """,item_dict=company_dict, primary_key='id', table='CYB_COMPANY')
        self.execute(result_sql, tuple_sql)
        return self.get_company(company_dict['id'])

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
        [result_sql, tuple_sql] = self._build_select_sql('project_id', project_id, 'CYB_IPO')
        self.execute(result_sql, tuple_sql)
        projects = self.cursor.fetchall()
        return projects

    def insert_or_update_ipo(self, project_dict) -> object:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""project_id, total_fund_rasing, stage, stage_status, biz_type, csrc_code, law_office_id, sponsor_id, sponsor_name, sponsor_code, accounting_firm_id,
            accounting_firm_name,rating_agency_id, rating_agency_name, accept_apply_date, law_office_name, asset_evaluation_institute_id, asset_evaluation_institute_name,
            company_id, update_date, create_date, company_name, stage_name, stage_status_name, issue_market, csrc_desc,
            accept_apply_time, update_time, create_time,sub_sponsor_id, sub_sponsor_name, sub_sponsor_code""",item_dict=project_dict, primary_key='project_id', table='CYB_IPO')
        self.execute(result_sql, tuple_sql)
        return self.get_ipo(project_dict['project_id'])

    def __get_process__(self, id, table) -> list:
        [result_sql, tuple_sql] = self._build_select_sql('id', id, table)
        self.execute(result_sql, tuple_sql)
        porcesses = self.cursor.fetchall()
        return porcesses

    def __insert_or_update_process__(self, dict, table, extra_key_string = '') -> object:
        key_string = """id, project_id, company_id, company_name, stage, stage_name, stage_status, stage_status_name, timestamp, date"""
        if extra_key_string != '':
            key_string += f',{extra_key_string}'
        [result_sql, tuple_sql] = self._build_sql_(key_string=key_string,item_dict=dict, primary_key='id', table=table)
        self.execute(result_sql, tuple_sql)
        return self.__get_process__(dict['id'], table)
    
    def get_milestone(self, milestone_id) -> list:
        return self.__get_process__(id=milestone_id, table='CYB_MILESTONE')

    def insert_or_update_milestone(self, milestone_dict) -> object:
        return self.__insert_or_update_process__(dict=milestone_dict, table='CYB_MILESTONE')

    
    def get_other(self, other_id) -> list:
        [result_sql, tuple_sql] = self._build_select_sql('id', other_id, 'CYB_OTHER')
        self.execute(result_sql, tuple_sql)
        others = self.cursor.fetchall()
        return others
        

    def insert_or_update_other(self, other_dict) -> object:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""id, project_id, company_id, company_name, timestamp, date, reason""",item_dict=other_dict, primary_key='id', table='CYB_OTHER')
        self.execute(result_sql, tuple_sql)
        return self.get_other(other_dict['id'])

    def get_file(self, file_id) -> list:
        [result_sql, tuple_sql] = self._build_select_sql('file_id', file_id, "CYB_FILE")
        self.execute(result_sql, tuple_sql)
        files = self.cursor.fetchall()
        return files

    def insert_or_update_file(self, file_dict) -> object:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""file_id, project_id, company_id, company_name, stage, stage_name, file_name, file_url, file_size, file_type_of_process, file_type_of_audit, file_type_of_process_desc, file_type_of_audit_desc, publish_time, publish_date""",item_dict=file_dict, primary_key='file_id', table='CYB_FILE')
        self.execute(result_sql, tuple_sql)
        return self.get_file(file_dict['file_id'])

    def get_intermediary(self, intermediary_id) -> list:
        [result_sql, tuple_sql] = self._build_select_sql('id', intermediary_id, "INTERMEDIARY")
        self.execute(result_sql, tuple_sql)
        intermediarys = self.cursor.fetchall()
        return intermediarys

    def insert_or_update_intermediary(self, intermediary_dict) -> object:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""project_id, intermediary_id, type, name, intermeidary_order""",item_dict=intermediary_dict, primary_key='id', table='INTERMEDIARY')
        self.execute(result_sql, tuple_sql)
        return self.get_intermediary(intermediary_dict['id'])

    
    def get_intermediary_item(self, project_id, intermediary_id) -> list:
        content = self.cursor.mogrify("""
        select * from \"CYB_INTERMEDIARY\" where project_id = %s and intermediary_id = %s;
        """, (str(project_id), str(intermediary_id), ),)
        self.cursor.execute(content)
        self.commit()
        files = self.cursor.fetchall()
        return files

    def insert_or_update_intermediary_item(self, item_dict) -> object:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""project_id, intermediary_id, type, name, intermediary_order""",item_dict=item_dict, primary_key='project_id, intermediary_id', table='CYB_INTERMEDIARY')
        self.execute(result_sql, tuple_sql)
        return self.get_intermediary_item(item_dict['project_id'], item_dict['intermediary_id'])
    
    def get_person_item(self, person_id) -> list:
        [result_sql, tuple_sql] = self._build_select_sql('id', person_id, "CYB_INTERMEDIARY_PERSON")
        self.execute(result_sql, tuple_sql)
        files = self.cursor.fetchall()
        return files

    def insert_or_update_person_item(self, person_dict) -> object:
        [result_sql, tuple_sql] = self._build_sql_(key_string="""project_id, intermediary_id, id, name, job_type, job_title""",item_dict=person_dict, primary_key='id', table='CYB_INTERMEDIARY_PERSON')
        self.execute(result_sql, tuple_sql)
        return self.get_person_item(person_dict['id'])

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