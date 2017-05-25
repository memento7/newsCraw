from scrapy.selector import Selector

from newsCraw.utils.scrapy_module import Scrapy_Module
from newsCraw.utils.requestable import Requestable, Request
from newsCraw.utils.utility import *

from urllib.parse import urlsplit
import json

class News_Naver(Scrapy_Module):
    def __init__(self):
        self.allow = ['https://www.instagram.com']
        self.url ='https://www.instagram.com/graphql/query/?query_id=17874545323001329&id={}&first=200'
        self.header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'ko,en;q=0.8,en-US;q=0.6,da;q=0.4,la;q=0.2',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        }

    #@Requestable
    def parser(self, keyword, date: str) -> Request:
        def get_instagram_id(keyword) -> str:
            pass

        key, sub = keyword
        
        return Request(self.url.format(query_filter(key), d, d), callback=self.parse_count, meta={'key': key})

    def dressor(self, tx, item: dict):
        """tx is dbpool object
        # Usage
        - tx.execute(query);
        - tx.fetchone()
        """
        pass