from typing import Tuple
import psycopg2
import psycopg2.extras
from crawler.util.postgre import PostgreConnect, PostgreConnector

class PostgreConnect():
    connector = None
    cursor = None
    def __init__(self, host = 'localhost', port = 5432, dbname = 'test_ipo', user = 'postgres') -> None:
        
        
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
    

postgre_link = PostgreConnect()


class ZBPostgreConnector(PostgreConnector):
    def __init__(self) -> None:
        super().__init__(postgre_link)
    
    def get_empty_ipo(self) -> bool:
        content = self.cursor.mogrify("""
            select * from \"ZB_IPO\" where total_fund_rasing = 0 or total_fund_rasing > 544 order by update_time desc;
        """, (),)
        self.cursor.execute(content)
        ipos = self.cursor.fetchall()
        return ipos
         
    def get_all_ipos(self) -> bool:
        content = self.cursor.mogrify("""
            select * from \"ZB_IPO\" order by update_time desc;
        """, (),)
        self.cursor.execute(content)
        ipos = self.cursor.fetchall()
        return ipos

    def is_ipo_existed(self, project_id) -> bool:
        projects = self.get_ipo(project_id)
        return len(projects) > 0
    
    def get_ipo(self, project_id) -> list:
        [result_sql, tuple_sql] = self._build_select_sql('project_id', project_id, 'ZB_IPO')
        self.execute(result_sql, tuple_sql)
        projects = self.cursor.fetchall()
        return projects

    def insert_ipo(self, project_dict) -> object:
        key_string = """project_id, total_fund_rasing, stage, csrc_code, sponsor_id, sponsor_name, sponsor_code,
            company_id, update_date, create_date, company_name, stage_name, issue_market, csrc_desc,issue_market_desc,
            update_time, create_time"""
        
        [result_sql, tuple_sql] = self._build_insert_sql_(key_string=key_string,item_dict=project_dict, primary_key='project_id', table='ZB_IPO')
        
        self.execute(result_sql, tuple_sql)
        return self.get_ipo(project_dict['project_id'])

    def update_ipo(self, project_dict, ks) -> object:
        key_string = ks if ks != '' else """project_id, total_fund_rasing, stage, csrc_code, sponsor_id, sponsor_name, sponsor_code,
            company_id, update_date, create_date, company_name, stage_name, issue_market, csrc_desc,issue_market_desc,
            update_time, create_time"""
        
        [result_sql, tuple_sql] = self._build_update_sql_(key_string=key_string,item_dict=project_dict, primary_key='project_id', table='ZB_IPO')
        print(result_sql, tuple_sql)
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
        [result_sql, tuple_sql] = self._build_insert_sql_(key_string=key_string,item_dict=dict, primary_key='id', table='ZB_PROCESS')
        content = self.cursor.mogrify(result_sql, tuple_sql)
        self.cursor.execute(content)
        return self.get_process(dict['id'])
    
    def get_ipo_lasted_file(self, project_id) -> object:
        [result_sql, tuple_sql] = self._build_select_sql('project_id', project_id, "ZB_FILE")
        self.execute(result_sql, tuple_sql)
        files = self.cursor.fetchall()
        return files

    def get_file(self, project_id) -> list:
        content = self.cursor.mogrify("""
            select * from \"ZB_FILE\" where project_id = %s order by publish_time;
        """, (project_id, ),)
        self.cursor.execute(content)
        file = self.cursor.fetchone()
        return file

    def insert_or_update_file(self, file_dict) -> object:
        [result_sql, tuple_sql] = self._build_insert_sql_(key_string="""file_id, project_id, company_id, company_name, stage, stage_name, file_name, file_url, file_type_of_process, file_type_of_audit, file_type_of_process_desc, file_type_of_audit_desc, publish_time, publish_date""",item_dict=file_dict, primary_key='file_id', table='ZB_FILE')
        content = self.cursor.mogrify(result_sql, tuple_sql)
        self.cursor.execute(content)
        return self.get_file(file_dict['file_id'])