from email.policy import default
from sqlite3 import converters
import attrs

from crawler.util.decorator import add_method
from crawler.util.util import to_dict, load_item, get_source_map, convert_time, get_today_str
from crawler.util.constant import STOCK_EXCHANGE_TYPE

@add_method('load_item', load_item)
@add_method('get_source_map', get_source_map)
@add_method("to_dict", to_dict)
class BaseItem:
    
    pass

@attrs.define
class MarketCountItem(BaseItem):
    time: int = attrs.field(default = 0,  metadata={'source': 'time'})

    count: int = attrs.field(default = -1, metadata={'source': 'count'})

    stock_exchange_type: int = attrs.field(default = None, metadata={'source': 'stock_exchange_type'}) # 上市交易所
    
    stock_exchange_desc: str = attrs.field(default = '', metadata={'source': 'stock_exchange_desc'}) # 上市交易所

    business_type: int = attrs.field(default = None, metadata={'source': 'business_type'}) # 上市交易所

    business_type_desc: str = attrs.field(default = '', metadata={'source': 'business_type_desc'})
    
    date: str = attrs.field(default = '', metadata={'source': 'date'})
    
    issue_market: int = attrs.field(default = '', metadata={'source': 'issue_market'}) # 上市交易所
    issue_market_desc: int = attrs.field(default = '', metadata={'source': 'issue_market_desc'}) # 上市交易所
    

class Field:
    def __init__(self, name, db_type, converter=None, description=None):
        self.name = name
        self.db_type = db_type
        self.converter_name = converter
        self.description = description

    def get_value(self, record):
        value = record.get(self.name)
        if value is None:
            return None
        if self.converter_name:
            converter = converters.get(self.converter_name)
            if converter:
                return converter(value)
        return self.convert_value(value)

    def convert_value(self, value):
        # Default conversion method
        return value


class Table:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

    def create_sql(self):
        fields_sql = []
        for field in self.fields:
            fields_sql.append(f"{field.name} {field.db_type}")
        fields_sql = ", ".join(fields_sql)
        return f"CREATE TABLE {self.name} ({fields_sql});"

    def insert_sql(self, record):
        values = []
        for field in self.fields:
            value = field.get_value(record)
            if value is None:
                values.append("NULL")
            elif isinstance(value, str):
                values.append(f"'{value}'")
            else:
                values.append(str(value))
        values_sql = ", ".join(values)
        return f"INSERT INTO {self.name} VALUES ({values_sql});"


def create_class(class_name, attribute1, attribute2):
    return type(class_name, (), {
        "attribute1": attribute1, 
        "attribute2": attribute2, 
        "say_hello": lambda self: print("Hello, I'm an instance of " + class_name)
    })