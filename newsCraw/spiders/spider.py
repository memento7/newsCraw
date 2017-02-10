# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.spiders import Spider
from newsCraw.items import newsCrawItem
from scrapy.http import Request
from scrapy.selector import Selector 

import calendar
class newsCrawSpider(scrapy.Spider):
    name = "newsCraw"
    allowed_domains = ['news.naver.com']
    url = "http://news.naver.com/main/search/search.nhn?"
    loaded = False
    page = 10
    skip_actor = False
    skip_y = False
    skip_m = False

    def query_filter(self, query):
        return ''.join([ '%' + hex(x)[2:] for x in query.encode('euc-kr')])

    def load(self):
        with open('./data/checkpoint.json', 'r') as file:
            self.data = json.load(file)
        with open('./data/actors.txt', 'r', encoding='UTF-8') as file:
            self.actors = file.readlines()
        print ('data loaded!')
        print (self.data)
        self.loaded = True

    def save(self, actor, y, m):
        self.data['actor'] = actor
        self.data['y'] = "%4d" % y
        self.data['m'] = "%2d" % m
        with open('./data/checkpoint.json', 'w') as file:
            json.dump(self.data, file)

    def loop(self):
        if not self.loaded:
            self.load()
        for actor in self.actors:
            actor = actor[1:].strip()
            if actor == self.data['actor']: self.skip_actor = True
            if not self.skip_actor: continue
            for y in range(1990, 2018):
                if str(y) == self.data['y']: self.skip_y = True
                if not self.skip_y: continue
                for m in range(1, 13):
                    if ("%2d" % m) == self.data['m']: self.skip_m = True
                    if not self.skip_m: continue
                    (_, e) = calendar.monthrange(y, m)
                    yield (actor.strip(), "%04d-%02d-%02d" % (y, m, 1), "%04d-%02d-%02d" % (y, m, e))
                self.save(actor, y, m)

    def start_requests(self):
        for query, sd, ed in self.loop():
            yield Request(self.url + "query=" + self.query_filter(query) + "&startDate=" + sd + "&endDate=" + ed, meta={'q': query, 'sd': sd, 'ed':ed}, callback = self.parse_count)
            
    def parse_count(self, response):
        count = Selector(response).xpath('//span[@class="result_num"]/text()').re(r'\/ (.+?)\건')
        count = count and min(int(int(count[0].replace(',', '')) / 10) + 1, 400) or 0
        for page in range(count):
            yield Request(self.url + "query=" + self.query_filter(response.meta['q']) + "&startDate=" + response.meta['sd'] + "&endDate=" + response.meta['ed'] + "&page=" + str(page), meta={'q': response.meta['q']}, callback = self.parse)

    def parse(self, response):
        items = []
        li = Selector(response).xpath('//ul[@class="srch_lst"]')
        for site in li:
            item = newsCrawItem()
            item['actor'] = response.meta['q']
            item['title'] = site.xpath('.//a[@class="tit"]').re(r'\>(.+?)\<\/a')[0]
            item['time'] = site.xpath('.//span[@class="time"]//text()').extract_first()
            item['press'] = site.xpath('.//span[@class="press"]//text()').extract_first()
            item['href_origin'] = site.xpath('.//a[@class="tit"]//@href').extract_first()
            item['href_naver'] = site.xpath('.//a[@class="go_naver"]//@href').extract_first()
            items.append(item)

        return items
