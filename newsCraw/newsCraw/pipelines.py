# -*- coding: utf-8 -*-
from newsCraw.utils.requestable import Requestable
from newsCraw.utils.utility import close_crawler

class newsCrawPipeline(object):
    def __init__(self):
        self.id = None

    def open_spider(self, spider):
        self.id = spider.id
        for allow in Requestable.allow():
            spider.allowed_domains += allow

        Requestable.init()

    def close_spider(self, spider): 
        for info in spider.infos:
            close_crawler(info, spider.date_start.strftime('%Y.%m.%d'), spider.date_end.strftime('%Y.%m.%d'), spider.id)
        Requestable.close()

    def process_item(self, item, spider):
        if 'MODULE' in item:
            name = item['MODULE']
            item['manage_id'] = self.id
            item = Requestable.dress(name)(item)
        return item
