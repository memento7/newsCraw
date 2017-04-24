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
    def __init__(self):
        pass
        
    def date_range(self):
        for date in (self.start_date + timedelta(n) for n in range((self.end_date-self.start_date).days)):
            yield date

    def start_requests(self):
        for allow in Requestable.allow():
            allowed_domains += allow

        for date in self.date_range():
            for keyword in self.keywords:
                for process in Requestable.process(keyword, date):
                    yield process