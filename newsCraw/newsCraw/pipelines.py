# -*- coding: utf-8 -*-
from twisted.enterprise import adbapi
from scrapy import signals

from newsCraw.utils.requestable import Requestable
from newsCraw import memento_settings as MS
from datetime import datetime, timedelta
import requests
import pymysql
import sys
import json

class newsCrawPipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('pymysql',
            **MS.SERVER_RDB_INFO,
            cursorclass = pymysql.cursors.DictCursor,
            cp_reconnect=True
        )

    def open_spider(self, spider):
        # TODO: get from api server
        def get_keywords(columns=['id', 'nickname', 'realname', 'subkey'], headers=MS.SERVER_API_HEADER):
            response = requests.get(MS.SERVER_API + 'entities/waiting', headers=headers)
            return [{c: k[c] for c in columns} for k in json.loads(response.text)]
        def get_data_range():
            return datetime(2017,4,25), datetime(2017,5,7)

        spider.keywords = [ " ".join([k['nickname'], k['subkey']]) for k in get_keywords()]
        spider.start_date, spider.end_date = get_data_range()

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        if 'MODULE' in item:
            res = self.dbpool.runInteraction(Requestable.dress(item['MODULE']), item)
            res.addErrback(self.db_error)
        return item

    def db_error(self, e):
        print ('Error', e)
