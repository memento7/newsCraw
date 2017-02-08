# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.spider import Spider 
from newsCraw.items import newsCrawItem
from scrapy.http import Request
from scrapy.selector import Selector 

import calendar
"%02d" % (1,)
class newsCrawSpider(scrapy.Spider):
    name = "newsCraw"
    allowed_domains = ['http://news.naver.com']
    loaded = False
    page = 10
    skip_actor = False
    skip_page = False
    skip_y = False
    skip_m = False
    url = "http://news.naver.com/main/search/search.nhn?"
    # start_urls = ["http://news.naver.com/main/search/search.nhn?query=%B1%E8%C5%C2%C8%F1&page="]

    def load(self):
        with open('./save.json', 'r') as file:
            self.data = json.load(file)

        with open('./actors.txt', 'r') as file:
            self.actors = file.readlines()
        self.loaded = True

    def save(self, actor, y, m):
        self.data['actor'] = actor
        self.data['y'] = "%4d" % y
        self.data['m'] = "%2d" % m
        with open('./save.json', 'w') as file:
            json.dump(self.data, file)

    def loop(self):
        if not self.loaded:
            self.load()

        for actor in self.actors:
            if actor == self.data['actor']: self.skip_actor = True
            if not self.skip_actor: continue
            for y in range(1990, 2016):
                if str(y) == self.data['y']: self.skip_y = True
                if not self.skip_y: continue
                for m in range(1, 13):
                    if str(m) == self.data['m']: self.skip_m = True
                    if not self.skip_m: continue
                    (_, e) = calendar.monthrange(y, m)
                    for page in range(1, 400):
                        yield (actor, page, "%04d%02d%02d" % (y, m, 1), "%04d%02d%02d" % (y, m, e))
                self.save(actor, y, m)

    def start_requests(self):
        for query, page, sd, ed in self.loop():
            yield Request(self.url + "query=" + query + "&page=" + str(page) + "&startDate=" + sd + "&endDate=" + ed, self.parse)

    def parse(self, response):
        items = []
        li = Selector(response).xpath('//ul[@class="srch_lst"]')
        for site in li:
            item = newsCrawItem()
            item['title'] = site.xpath('.//a[@class="tit"]').re(r'\>(.+?)\<\/a')[0]
            item['press'] = site.xpath('.//span[@class="press"]//text()').extract_first()
            item['href'] = site.xpath('.//a[@class="go_naver"]//@href').extract_first()            
            items.append(item)

        return items
