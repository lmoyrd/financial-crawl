
import json

from typing import Callable, Iterable



def add_method(name, func):
    """
    给class增加目标方法
    """
    def wrapper(K):
        setattr(K, name, func)
        return K
    return wrapper

def inject_config(func) -> None:
    """
    给spider注入外部录入的config
    """
    def wrap(self, config=None, *args, **kwargs):
        if config != None:
            config_dict = json.loads(config)
            if config_dict != None and len(config_dict.keys()) > 0:  
                for key in config_dict.keys():
                    setattr(self, key, config_dict[key])
        func(self)
    return wrap

def wrap_extend_enum(enum_type):
    """
    集成枚举
    """
    def extend_enum(parent_enum: enum_type) -> Callable[[enum_type], enum_type]:
        def wrapper(extended_enum: enum_type) -> enum_type:
            joined = {}
            for item in parent_enum:
                joined[item.name] = (item.value, item.desc)
            for item in extended_enum:
                joined[item.name] = (item.value, item.desc)
            return enum_type(extended_enum.__name__, joined)
        return wrapper
    return extend_enum