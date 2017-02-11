# -*- coding: utf-8 -*-
import json
import re
from datetime import datetime, timedelta
class newsContentCrawPipeline(object):
    pat_rl = [re.compile('\\n'), re.compile('\\t')]
    pat_dl = [re.compile('\n\/\/')]

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def dl_filter(self, content):
        ret = False
        for pat in self.pat_dl:
            ret = ret or pat.match(content)
        return ret

    def content_filter(self, content):
        content = ''.join([ cont for cont in content if not self.dl_filter(cont) ])

        for pat in self.pat_rl:
            content = re.sub(pat, '', content)

        return content

    def process_item(self, item, spider):
        item['content'] = self.content_filter(item['content'])
        return item
