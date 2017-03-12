# -*- coding: utf-8 -*-
import scrapy

class newsCrawItem(scrapy.Item):
    href = scrapy.Field()
    href_naver = scrapy.Field()
    keyword = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    published_time = scrapy.Field()
    crawled_time = scrapy.Field()
    oid = scrapy.Field()
    aid = scrapy.Field()
    comments = scrapy.Field()
    reply_count = scrapy.Field()
    # author = scrapy.Field()
    # content = scrapy.Field()
    # reply_count = scrapy.Field()
    # sympathy_count = scrapy.Field()
    # antipathy_count = scrapy.Field()
    # mod_time = scrapy.Field()
    # crawled_time = scrapy.Field()
