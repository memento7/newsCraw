# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.spiders import Spider
from newsContentCraw.items import newsContentCrawItem
from scrapy.http import Request
from scrapy.selector import Selector 
import pandas as pd
import math

class newsContentCrawSpider(scrapy.Spider):
    name = "newsContentCraw"
    allowed_domains = ['news.naver.com']
    loaded = False
    url = "http://news.naver.com/main/search/search.nhn?"

    def load(self):
        self.frame = pd.read_csv('../data/actor_href.csv', encoding='cp949')
        with open('./checkpoint.json', 'r') as file:
            self.data = json.load(file)
        print ('data loaded!')
        print (self.data)
        self.loaded = True

    def save(self, idx):
        self.data['idx'] = int(idx)
        with open('./checkpoint.json', 'w') as file:
            json.dump(self.data, file)

    def loop(self):
        if not self.loaded:
            self.load()
        for idx, data in self.frame.iterrows():
            if idx < self.data['idx']: continue
            if type(data.values[2]) is str:
                yield data.values[4], data.values[2]
            self.save(idx)

    def start_requests(self):
        for actor, href in self.loop():
            yield Request(href, meta={'actor': actor}, callback = self.parse)
            
    def parse(self, response):
        article = Selector(response).xpath('//div[@id="articleBodyContents"]')

        item = newsContentCrawItem()
        item['actor'] = response.meta['actor']
        item['href'] = response.url
        item['content'] = article.xpath('.//text()').extract()

        return item
