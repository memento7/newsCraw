# -*- coding: utf-8 -*-
from newsCraw.utils.requestable import Requestable
from newsCraw.utils.connection import get_daterange, get_keywords, get_type_id, put_item

class newsCrawPipeline(object):
    def __init__(self):
        pass

    def open_spider(self, spider):
        for allow in Requestable.allow():
            spider.allowed_domains += allow

        Requestable.init()

        spider.keywords = get_keywords()
        spider.start_date, spider.end_date = get_daterange()

    def close_spider(self, spider):
        Requestable.close()

    def process_item(self, item, spider):
        if 'MODULE' in item:
            name = item['MODULE']
            item = Requestable.dress(name)(item)
            put_item(item, Requestable.info(name), name.lower())
        return item
