# -*- coding: utf-8 -*-
import scrapy
from scrapy.spider import Spider 
from newsCraw.items import newsCrawItem
from scrapy.http import Request
from scrapy.selector import Selector 

class newsCrawSpider(scrapy.Spider):
    name = "newsCraw"
    allowed_domains = ['http://news.naver.com']
    start_urls = ["http://news.naver.com/main/search/search.nhn?query=%C0%CC%C8%BF%B8%AE&page=0"]

    def parse(self, response):
        items = []

        for site in Selector(response).xpath('div['srch_result_area']//ul[@class="srch_lst"]/li'):
            item = newsCrawItem()
            texts = site.xpath('//text()').extract()
            for text in texts:
                print (text)
            item['title'] = site.xpath('//a[@class="tit"]//text()').extract()
            item['press'] = site.xpath('//span[@class="press"]//text()').extract()
            item['href'] = site.xpath('//a[@class="go_naver"]//@href').extract()
            
            items.append(item)

        return items