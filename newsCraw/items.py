# -*- coding: utf-8 -*-
import scrapy
from scrapy.item import Item, Field


class newsCrawItem(scrapy.Item):
    title = scrapy.Field()
    press = scrapy.Field()
    href = scrapy.Field()

