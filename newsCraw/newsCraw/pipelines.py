# -*- coding: utf-8 -*-
from newsCraw.utils.requestable import Requestable
from newsCraw.utils.connection import get_daterange, get_keywords, get_type_id, put_item

class newsCrawPipeline(object):
    def __init__(self):
        self.subkeys = dict()
        pass

    def open_spider(self, spider):
        def get_subkey(cname, keywords):
            return { keyword: {
                        subkey: get_type_id({
                            'keyword': keyword,
                            'subkey': subkey
                        }, cname) for subkey in [info['subkey']]
                    } for keyword, info in keywords.items()}

        for allow in Requestable.allow():
            spider.allowed_domains += allow

        Requestable.init()

        spider.keywords = get_keywords()
        for module in Requestable.i.keys():
            self.subkeys[module] = get_subkey(module, spider.keywords)

        spider.start_date, spider.end_date = get_daterange()

    def close_spider(self, spider):
        Requestable.close()

    def process_item(self, item, spider):
        if 'MODULE' in item:
            name = item['MODULE']
            item = Requestable.dress(name)(item)
            keyword = item['information']['keyword']
            subkey = item['information']['subkey']
            put_item(item, self.subkeys[name][keyword][subkey], name.lower())
        return item
