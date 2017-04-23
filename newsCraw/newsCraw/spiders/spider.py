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
from datetime import datetime

class newsCrawSpider(scrapy.Spider):
    name = "newsCraw"
    allowed_domains = ['news.naver.com', 'apis.naver.com', 'entertain.naver.com', 'sports.news.naver.com']

    def start_requests(self):
        for allow in Requestable.allow():
            allowed_domains += allow

        for process in Requestable.process('김태희', '2015-02-03', '2015-03-03'):
            yield process