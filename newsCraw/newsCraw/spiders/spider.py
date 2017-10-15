# -*- coding: utf-8 -*-
from os.path import isfile
import calendar
import json
from datetime import datetime, timedelta

import scrapy
from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector

from newsCraw.items import newsCrawItem
from newsCraw.utils.requestable import Requestable
from newsCraw.utils.utility import get_subkey, start_crawler, close_crawler
from newsCraw.utils.connection import get_entities
from newsCraw.utils.logger import log

class newsCrawSpider(scrapy.Spider):
    name = "newsCraw"
    allowed_domains = []

    def __init__(self, *args, **kwargs):
        if all(key in kwargs for key in ['entity', 'date_start', 'date_end', 'id']):
            self.id = kwargs['id']
            self.entity = kwargs['entity']
            self.date_start = datetime.strptime(kwargs['date_start'], "%Y.%m.%d")
            self.date_end = datetime.strptime(kwargs['date_end'], "%Y.%m.%d")
            log('init with {}, {} to {}'.format(self.entity, self.date_start, self.date_end))
        else:
            self.id = 'not init'
            self.entity = None
            self.date_start = datetime(2000,1,1)
            self.date_end = datetime(2017,6,2)

    def push_data(self):
        for entity, subkeys in [(self.entity, get_subkey(self.entity))] if self.entity else get_entities():
            info = start_crawler(entity, self.date_start.strftime('%Y.%m.%d'), self.date_end.strftime('%Y.%m.%d'), self.id)
            if not info:
                continue
            log(info + ' started!')
            if not subkeys:
                subkeys.append('')
            for subkey in subkeys:
                log('start ' + entity + ' ' + subkey)
                for date in (self.date_start + timedelta(n) for n in range(1 + (self.date_end-self.date_start).days)):
                    yield {
                        'keyword': entity,
                        'subkey': subkey,
                        'date': date.strftime('%Y-%m-%d'),
                    }
            close_crawler(info, self.date_start.strftime('%Y.%m.%d'), self.date_end.strftime('%Y.%m.%d'), self.id)

    def start_requests(self):
        for data in self.push_data():
            for process in Requestable.process(data):
                yield process
