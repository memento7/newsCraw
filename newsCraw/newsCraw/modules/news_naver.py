from scrapy.selector import Selector

from newsCraw.utils.scrapy_module import Scrapy_Module
from newsCraw.items import newsCrawItem
from newsCraw.utils.requestable import Requestable, Request
from newsCraw.utils.utility import *

import json

class News_Naver(Scrapy_Module):
    def __init__(self):
        self.url = "http://news.naver.com/main/search/search.nhn?query={}&startDate={}&endDate={}"
        self.crl = "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&lang=ko&pool=cbox5&objectId=news{}%2C{}"

    @Requestable
    def process_count(self, keyword: str, start_date: str, end_date: str) -> Request:
        return Request(self.url.format(query_filter(keyword), start_date, end_date), callback=self.parse_count, meta={'key': keyword})

    def parse_count(self, response):
        def get_count(text):
            count = text.re(r'\/ (.+?)\건')
            count = int(count[0].replace(',', '')) or 0
            return min(count / 10 + 1, 400)
        count = get_count(Selector(response).xpath('//span[@class="result_num"]/text()'))
        key = response.meta['key']
        for page in range(int(count)):
            yield Request(response.url + "&page=" + str(page), callback=self.parse_title, meta={'key': key})

    def parse_title(self, response):
        for site in Selector(response).xpath('//ul[@class="srch_lst"]'):
            item = {}
            item['keyword'] = response.meta['key']
            item['title'] = site.xpath('.//a[@class="tit"]').re(r'\>(.+?)\<\/a')[0]
            item['published_time'] = site.xpath('.//span[@class="time"]//text()').extract_first()
            item['crawled_time'] = now()
            item['href'] = site.xpath('.//a[@class="tit"]//@href').extract_first()
            item['href_naver'] = site.xpath('.//a[@class="go_naver"]//@href').extract_first()

            if item['href_naver']:
                params = parse_param(item['href_naver'])
                item['oid'] = params['oid']
                item['aid'] = params['aid']
                yield Request(item['href_naver'], callback=self.parse_content, meta={'item': item})
            return item

    def parse_content(self, response):
        item = response.meta['item']
        news_naver = Selector(response).xpath('//div[@id="articleBodyContents"]').xpath('.//text()').extract()
        entertain = Selector(response).xpath('//div[@id="articeBody"]').xpath('.//text()').extract()
        sports = Selector(response).xpath('//div[@id="newsEndContents"]').xpath('.//text()').extract()

        item['content'] = news_naver + entertain + sports
        yield Request(self.crl.format(item['oid'], item['aid']), headers={'Referer': item['href_naver']}, callback=self.parse_reply, meta={'item': item})

    def parse_reply(self, response):
        params = parse_param(response.url)
        oid, aid = params['objectId'][4:].split('%2C')
        res = json.loads(response.body[10:-2].decode('utf-8'))

        if res['success']:
            result = res['result']
            item = response.meta['item']
            item['reply_count'] = result['count']['total']
            item['comments'] = []

            col_label = ['reply_count', 'mod_time', 'content', 'sympathy_count', 'antipathy_count', 'author']
            col_find = ['replyCount', 'modTime', 'contents', 'sympathyCount', 'antipathyCount', 'maskedUserId']

            for comment in result['commentList']:
                com = {'crawled_time': now()}
                for label, find in zip(col_label, col_find):
                    com[label] = comment[find]

                item['comments'].append(com)

            return self.dress(item)

    def dress(self, item):
        item['title'] = title_filter(item['title'])
        item['content'] = content_filter(item['content'])
        item['published_time'] = date_filter(item['published_time'])

        return item