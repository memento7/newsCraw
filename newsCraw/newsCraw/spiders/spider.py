# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Spider
from newsCraw.items import newsCrawItem
from scrapy.http import Request
from scrapy.selector import Selector

class newsCrawSpider(scrapy.Spider):
    name = "newsCraw"
    allowed_domains = ['news.naver.com']
    url = "http://news.naver.com/main/search/search.nhn?"

    def __init__(self):
        print ('spider init')
        pass

    def loop(self):
        print (self.do)
        for i in range(10):
            print ('loop call ' + str(i))
            yield i

    def start_requests(self):
        for idx in self.loop():
            yield Request(self.url + str(idx), callback = self.parse)
            
    def parse(self, response):
        article = Selector(response).xpath('//div[@id="articleBodyContents"]')

        item = newsCrawItem()
        item['keyword'] = 'actor'
        item['href_naver'] = response.url
        item['content'] = 'content'

        return item
