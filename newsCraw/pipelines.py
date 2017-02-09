# -*- coding: utf-8 -*-
import json
import re
from datetime import datetime, timedelta
class newsCrawPipeline(object):
    pat_time = re.compile(r'(\d+?)\일\전')

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_time(self, time):
        match = self.pat_time.match(time) 
        if match:
            d = int(match.group(1))
            return (datetime.today() - timedelta(days = d)).strftime("%Y.%m.%d")
        return time

    def process_item(self, item, spider):
        item['time'] = self.process_time(item['time'])
        return item
