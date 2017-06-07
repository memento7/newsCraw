# -*- coding: utf-8 -*-
from newsCraw.utils.requestable import Requestable

class newsCrawPipeline(object):
    def __init__(self):
        self.id = None

    def open_spider(self, spider):
        self.id = spider.id
        for allow in Requestable.allow():
            spider.allowed_domains += allow

        Requestable.init()

    def close_spider(self, spider):
        Requestable.close()

    def process_item(self, item, spider):
        if 'MODULE' in item:
            name = item['MODULE']
            item['manage_id'] = self.id
            item = Requestable.dress(name)(item)
        return item
