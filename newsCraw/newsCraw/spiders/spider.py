# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector

from newsCraw.items import newsCrawItem
from newsCraw.utils.requestable import Requestable

from os.path import isfile
import calendar
import json
from datetime import datetime, timedelta

class newsCrawSpider(scrapy.Spider):
    name = "newsCraw"
    allowed_domains = []

    keywords = []
    start_date = ''
    end_date = ''

    def __init__(self):
        pass

    def push_data(self):
        for keyword, info in self.keywords.items():
            subkey = info['subkey']
            for date in (self.start_date + timedelta(n) for n in range((self.end_date-self.start_date).days)):
                yield {
                    'keyword': keyword,
                    'subkey': subkey,
                    'date': date,
                }

    def start_requests(self):
        for data in self.push_data():
            for process in Requestable.process(data):
                yield process
