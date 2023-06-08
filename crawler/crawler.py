# -*- coding: utf-8 -*-

from ast import arg
import json
import datetime as dt
import argparse
import re
import os
from multiprocessing import Queue, Process

from twisted.internet import reactor
from twisted.internet.defer import Deferred, inlineCallbacks

from crawler.util import util

argv_parser = argparse.ArgumentParser()

'''
runfile('文件路径', args='-t="10:56"', wdir='文件路径')
'''
argv_parser.add_argument('-t','--time', default='9:00', help='定时抓取时间，默认是9点') # 2 17:13
argv_parser.add_argument('-da','--download-all', default=False, type=bool, help='是否强制抓取所有数据，默认为否，只更新有变更的数据')
argv_parser.add_argument('-e','--env', default='dev',  help='启动环境') # dev online
argv_parser.add_argument('-ra','--remove-all', default=False,  type=bool, help='删除所有数据') # dev online
argv_parser.add_argument('-rao','--remove-all-only', default=False,  type=bool, help='仅删除数据')
argv_parser.add_argument('-d','--debug', default=False,  type=bool, help='打印日志') # dev online
# 使用 action='store_true' 或 action='store_false' 来指定参数是否为真或假。如果指定了 -sn 参数，则 start_now 的值为 True，否则 start_now 的值为 False。如果不指定 action 参数，则默认为 action='store'，会将参数解析为字符串。
argv_parser.add_argument('-sn','--start-now', action='store_true', help='是否立即开始，默认不是') # 2 17:13
spider_conf = {}

def load_spiders():
    '''
    Load all scrapy spiders

    Returns
    -------
    spider_classes : All Scrapy Spiders, can be started by reactor call

    '''
    from scrapy import spiderloader
    from scrapy.utils.project import get_project_settings
    settings = get_project_settings()
    spider_loader = spiderloader.SpiderLoader.from_settings(settings)
    spiders = spider_loader.list()
    spider_names = [name for name in spiders]
    print('spider_names', spider_names)
    return spider_names

def crawl_result(result):
    print('crawl_result', result)


def crawl_job():
    """
    Job to start spiders.
    Return Deferred, which will execute after crawl has completed.
    """
    from scrapy.crawler import CrawlerRunner
    from scrapy.utils.log import configure_logging
    from scrapy.utils.project import get_project_settings
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    spiders = load_spiders()
    deferred = Deferred()
    # 按顺序执行所有cralwer
    @inlineCallbacks
    def crawl_spider(idx):
        idx += 1
        if idx < len(spiders):
            crawler = runner.create_crawler(spiders[idx])
            # 将部分数据维护到crawler中，用于后续匹配
            #print('crawler setting', crawler.settings.copy_to_dict())
            yield runner.crawl(crawler, config=json.dumps(spider_conf))
            # TODO: 查询当前redis数据，传到下个crawler中，
            # 这样，从kcb整体爬虫在pipeline中查询得到所有有修改的记录，存到redis中
            # 此爬虫执行后，kcb_detail爬虫获取这部分数据，在pipeline中检测当前是自己的执行过程，则从redis中取到这部分数据，并进行爬虫，然后删除redis中的数据，也可以直接存着，以时间为key存着，然后写到postgres中
            crawl_spider(idx)
        else:
            deferred.callback(True)
    
    crawl_spider(-1)
    return deferred

def schedule_next_crawl_interval(null, sleep_time):
    """
    Schedule the next crawl
    """
    reactor.callLater(sleep_time, crawl_interval)

def crawl_interval():
    """
    A "recursive" function that schedules a crawl 30 seconds after
    each successful crawl.
    """
    # crawl_job() returns a Deferred
    spiders = load_spiders()
    d = crawl_job(spiders[0])
    # call schedule_next_crawl(<scrapy response>, n) after crawl job is complete
    d.addCallback(schedule_next_crawl_interval, 60)
    d.addErrback(catch_error)

def schedule_next_crawl_schedule(null, hour, minute):
 
    tomorrow = (
        dt.datetime.now() + dt.timedelta(days=1)
        ).replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    sleep_time = (tomorrow - dt.datetime.now()).total_seconds()
    print('next time:', sleep_time)
    reactor.callLater(sleep_time, crawl_schedule, [hour, minute])

def crawl_schedule(time):
    """
    crawl everyday at 1pm
    """
    
    # for spider in spiders:
    #     deferred = crawl_job(spider)
    #     deferred.addCallback(schedule_next_crawl_schedule, hour=0, minute=33)
    #     deferred.addErrback(catch_error)
    d = crawl_job()
    # crawl everyday at 1pm
    d.addCallback(schedule_next_crawl_schedule, hour=time[0], minute=time[1])
    d.addErrback(catch_error)
    #d.addBoth(lambda _: reactor.stop())
    return d

def catch_error(failure):
    print(failure.value)


if __name__=="__main__":
    args = argv_parser.parse_args()
    os.environ['SCRAPY_ENV'] = args.env
    if args.remove_all_only == True:
        util.delete_all_records()
    else:
        # Namespace => dict
        # args_dict = vars(args)
        [hour, minute] = util.get_time_in_array(args.time)
        spider_conf['download_all'] = args.download_all
        spider_conf['remove_all'] = args.remove_all

        now = args.start_now
        sleep_time = 0
        if hour >= 0 and minute >= 0:
            print(hour, minute)
            next_date_time = dt.datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            next_time = (next_date_time - dt.datetime.now().replace(microsecond=0)).total_seconds()
            if next_time <0:
                tomorrow = (
                    dt.datetime.now() + dt.timedelta(days=1)
                    ).replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                sleep_time = (tomorrow - dt.datetime.now()).total_seconds()
            elif next_time == 0:
                sleep_time = 1
            else:
                sleep_time = next_time
            
        if now:
            sleep_time = 1
        start_time = sleep_time # if next_time > 0 else 0
        print('next_time', sleep_time)
        deferred = Deferred()
        deferred.addCallback(crawl_schedule)
        reactor.callLater(start_time, deferred.callback,[hour, minute])
        reactor.run()
    