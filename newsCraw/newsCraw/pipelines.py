# -*- coding: utf-8 -*-

from scrapy import signals
from scrapy.utils.project import get_project_settings
from newsCraw.utils.requestable import Requestable

from twisted.enterprise import adbapi
import pymysql
import sys

SETTINGS = get_project_settings()

class newsCrawPipeline(object):
    def __init__(self):
        pass

    def set_names(self, tx):
        print (result)

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        return item
