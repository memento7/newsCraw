# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector

from newsCraw.items import newsCrawItem
from newsCraw.utils.requestable import Requestable
from newsCraw.utils.connection import get_entities

from os.path import isfile
import calendar
import json
from datetime import datetime, timedelta

class newsCrawSpider(scrapy.Spider):
    name = "newsCraw"
    allowed_domains = []

    def __init__(self, *args, **kwargs):
        if all(key in kwargs for key in ['keyword', 'date_start', 'date_end']):
            self.keyword = kwargs['keyword']
            self.date_start = datetime.strptime(kwargs['date_start'], "%Y-%m-%d")
            self.date_end = datetime.strptime(kwargs['date_end'], "%Y-%m-%d")
            print('init with {}, {} to {}'.format(self.keyword, self.date_start, self.date_end))
        else:
            pass

    def push_data(self):
        self.date_start = datetime(2000,1,1)
        self.date_end = datetime(2017,6,2)

        for entity, subkey in get_entities():
            print('start', entity, subkey)
            for date in (self.date_start + timedelta(n) for n in range(1 + (self.date_end-self.date_start).days)):
                yield {
                    'keyword': entity,
                    'subkey': subkey,
                    'date': date.strftime('%Y-%m-%d'),
                }

    def start_requests(self):
        for data in self.push_data():
            for process in Requestable.process(data):
                yield process
