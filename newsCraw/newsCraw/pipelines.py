# -*- coding: utf-8 -*-
from newsCraw.utils.requestable import Requestable

class newsCrawPipeline(object):
    def __init__(self):
        pass

    def open_spider(self, spider):
        for allow in Requestable.allow():
            spider.allowed_domains += allow

        Requestable.init()

        # spider.keywords = dict(filter(lambda x: x[0] in ['김무성', '박근혜', '문재인', '최순실'], get_entities().items()))
        # for module in Requestable.i.keys():
        #     self.subkeys[module] = get_subkey(module, spider.keywords)
        # spider.start_date, spider.end_date = get_daterange()

    def close_spider(self, spider):
        Requestable.close()

    def process_item(self, item, spider):
        if 'MODULE' in item:
            name = item['MODULE']
            item = Requestable.dress(name)(item)
        return item
