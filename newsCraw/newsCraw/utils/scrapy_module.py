from newsCraw.utils.requestable import Requestable, Request

class Scrapy_Module:
    allow = ['https://allow.domain']
    def __init__(self):
        pass

    def parser(self, response):
        return {'item': 'this is item'}

    # @Requestable
    def request(self, keyword, start_date, end_date):
        yield Request('', callback=self.parser, meta={'key':' key'})
