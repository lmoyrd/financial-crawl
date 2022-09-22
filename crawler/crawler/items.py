# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    
    companyName = scrapy.Field()
    status = scrapy.Field()
    stockMarket = scrapy.Field()
    sponsoringInstitution = scrapy.Field()
    disclosureTime = scrapy.Field()
    disclosureInfos = scrapy.Field()
    
    downloadInfoSource = scrapy.Field()
    downloadInfo = scrapy.Field()
    downloadType = scrapy.Field()
    crawlSource = scrapy.Field()
    crawlTime = scrapy.Field()
    crawlTimeString = scrapy.Field()

    count = scrapy.Field()
    pass

