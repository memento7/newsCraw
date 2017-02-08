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
        hxs = Selector(response).xpath('div[@id="srch_result_area"]//ul[@class="srch_lst"]/li')

            
        for site in Selector(response).xpath('div[@class="srch_result_area"]//ul[@class="srch_lst"]/li'):
            item = newsCrawItem()
            item['title'] = site.xpath('//a[@class="tit"]//text()').extract()
            item['press'] = site.xpath('//span[@class="press"]//text()').extract()
            item['href'] = site.xpath('//a[@class="go_naver"]//@href').extract()
            
            items.append(item)

        return items