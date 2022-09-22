# -*- coding: utf-8 -*-

import scrapy
import json

class BaseSpider(scrapy.Spider):
    
    def __init__(self, config=None, *args, **kwargs):
        if config != None:
            config_dict = json.loads(config)
            if config_dict != None and len(config_dict.keys()) > 0:  
                for key in config_dict.keys():
                    setattr(self, key, config_dict[key])

   