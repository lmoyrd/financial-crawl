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
    # time: int = attrs.field(default = None)

    count: int = attrs.field(default = None, metadata={'source': 'count'})

    stock_exchange_type: int = attrs.field(default = None, metadata={'source': 'stock_exchange_type'}) # 上市交易所
    
    @property
    def stock_exchange_type_desc(self):
        return STOCK_EXCHANGE_TYPE(self.stock_exchange_type).desc if self.stock_exchange_type else ''
    pass

    date: str = attrs.field(default = '', converter = get_today_str)
    
    @property
    def time(self):
        if self.date != None and self.date != '':
            result = convert_time(self.date)
            return result if result != '' else -1

    