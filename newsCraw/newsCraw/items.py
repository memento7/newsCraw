# -*- coding: utf-8 -*-
import scrapy


class newsCrawItem(scrapy.Item):
    keyword = scrapy.Field()
    href_origin = scrapy.Field()
    href_naver = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    time = scrapy.Field()
    press = scrapy.Field()