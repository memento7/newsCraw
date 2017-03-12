# -*- coding: utf-8 -*-

from scrapy import log
from scrapy import signals
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

class newsCrawPipeline(object):

    def __init__(self):
        pass

    def open_spider(self, spider):
        print ('open spider call')
        spider.do = '1'
        pass

    def close_spider(self, spider):
        print ('close spider call')
        pass

    def process_item(self, item, spider):
        print ('process item call')
        return item
