from newsCraw.utils.requestable import Requestable, Request

from datetime import datetime
from typing import Iterator

class Scrapy_Module:
    def __init__(self):
        """you must add crawling doamin to self.allow.
if you not, crawling do not work
        """
        self.allow = ['https://allow.domain']

    @property
    def info(self):
        pass

    def parser(self, response) -> Iterator[dict]:
        """if you finish making item, hand over to self.dress
if you need, you can yield Request in parser function
        """
        return self.dress({'item': 'this is item'})

    # @Requestable
    """you must decorate entry point of request.
if you have multiple entry points, We will do it in parallel.
    """
    def request(self, data: dict) -> Iterator[Request]:
        """Requestable function argument must be keyword, date for crawling
        """
        yield Request('', callback=self.parser, meta={'key': 'value'})

    def dress(self, item: dict) -> dict:
        """DO NOT OVERRIDE DRESS.
if you do, you must assign item['MODULE'] = self.__class__.__name__
        """
        item['MODULE']=self.__class__.__name__
        return item

    def dressor(self, item: dict) -> dict:
        """tx is dbpool object
        """
        return item