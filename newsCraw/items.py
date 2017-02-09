# -*- coding: utf-8 -*-
import scrapy
from scrapy.item import Item, Field


class newsCrawItem(scrapy.Item):
    actor = scrapy.Field()
    title = scrapy.Field()
    time = scrapy.Field()
    press = scrapy.Field()
    href_origin = scrapy.Field()
    href_naver = scrapy.Field()

