# -*- coding: utf-8 -*-
import scrapy


class newsContentCrawItem(scrapy.Item):
    actor = scrapy.Field()
    href = scrapy.Field()
    content = scrapy.Field()
