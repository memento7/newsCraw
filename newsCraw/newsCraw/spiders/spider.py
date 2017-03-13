# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Spider
from newsCraw.items import newsCrawItem
from scrapy.http import Request
from scrapy.selector import Selector
from os.path import isfile
import calendar
import json
from datetime import datetime

def now():
    return str(datetime.now())

def query_filter(query):
    return ''.join([ '%' + hex(x)[2:] for x in query.encode('euc-kr')])

def get_params(href):
    s = not '?' in href and [] or [ x.split('=') for x in href.split('?')[1].split('&')]
    return { p[0]: p[1] for p in s }

class newsCrawSpider(scrapy.Spider):
    name = "newsCraw"
    allowed_domains = ['news.naver.com', 'apis.naver.com', 'entertain.naver.com', 'sports.news.naver.com']
    url = "http://news.naver.com/main/search/search.nhn?"
    curl = "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&lang=ko&pool=cbox5&objectId="
    skip_data = {}

    def load(self):
        if isfile('./checkpoint.json'): 
            with open('./checkpoint.json', 'r') as file:
                self.skip_data = json.load(file)
            print ('data loaded!')

    def save(self, keyword, year, month):
        data = {}
        data['keyword'] = keyword
        data['year'] = year
        data['month'] = month
        with open('./checkpoint.json', 'w') as file:
            json.dump(data, file)

    def loop(self):
        self.load()
        for keyword in self.keywords[('keyword' in self.skip_data and self.skip_data['keyword'] in self.keywords) and self.keywords.index(self.skip_data['keyword']) or 0:]:
            for year in range('year' in self.skip_data and self.skip_data['year'] or 1990, 2018):
                for month in range('month' in self.skip_data and self.skip_data['month'] or 1, 13):
                    (_, e) = calendar.monthrange(year, month)
                    for day in range(1, e + 1):
                        yield (keyword, "%04d-%02d-%02d" % (year, month, day), "%04d-%02d-%02d" % (year, month, day))
                    self.save(keyword, year, month)
                if 'month' in self.skip_data: del self.skip_data['month']
            if 'year' in self.skip_data: del self.skip_data['year']

    def start_requests(self):
        for query, sd, ed in self.loop():
            yield Request(self.url + "query=" + query_filter(query) + "&startDate=" + sd + "&endDate=" + ed, meta={'q': query, 'sd': sd, 'ed':ed}, callback = self.parse_count)
            
    def parse_count(self, response):
        count = Selector(response).xpath('//span[@class="result_num"]/text()').re(r'\/ (.+?)\건')
        count = count and min(int(int(count[0].replace(',', '')) / 10) + 1, 400) or 0
        for page in range(count):
            yield Request(response.url + "&page=" + str(page), meta={'q': response.meta['q']}, callback = self.parse_title)

    def parse_title(self, response):
        for site in Selector(response).xpath('//ul[@class="srch_lst"]'):
            item = newsCrawItem()
            item['keyword'] = response.meta['q']
            item['title'] = site.xpath('.//a[@class="tit"]').re(r'\>(.+?)\<\/a')[0]
            item['published_time'] = site.xpath('.//span[@class="time"]//text()').extract_first()
            item['crawled_time'] = now()
            item['href'] = site.xpath('.//a[@class="tit"]//@href').extract_first()
            item['href_naver'] = site.xpath('.//a[@class="go_naver"]//@href').extract_first()

            if item['href_naver']:
                params = get_params(item['href_naver'])
                item['oid'] = params['oid']
                item['aid'] = params['aid']

                req_content = Request(item['href_naver'], callback = self.parse_content)
                req_content.meta['item'] = item
                yield req_content

            else:
                item['content'] = ""
                item['oid'] = 0
                item['aid'] = 0
                item['reply_count'] = 0
                yield item

    def parse_content(self, response):
        item = response.meta['item']

        news_naver = Selector(response).xpath('//div[@id="articleBodyContents"]').xpath('.//text()').extract()
        entertain = Selector(response).xpath('//div[@id="articeBody"]').xpath('.//text()').extract()
        sports = Selector(response).xpath('//div[@id="newsEndContents"]').xpath('.//text()').extract()
        item['content'] = news_naver + entertain + sports

        req_comment = Request(self.curl + "news" + item['oid'] + "%2C" + item['aid'], headers={'Referer': item['href_naver']}, callback = self.parse_comment)
        req_comment.meta['item'] = item

        yield req_comment

    def parse_comment(self, response):
        body = response.body
        res = json.loads(body[10:-2].decode('utf-8'))

        if res['success']:
            result = res['result']

            item = response.meta['item']
            item['reply_count'] = result['count']['total']
            item['comments'] = []

            col_label = ['reply_count', 'mod_time', 'content', 'sympathy_count', 'antipathy_count', 'author']
            col_find = ['replyCount', 'modTime', 'contents', 'sympathyCount', 'antipathyCount', 'maskedUserId']

            for comment in result['commentList']:
                com = {}
                for label, find in zip(col_label, col_find):
                    com[label] = comment[find]
                item['comments'].append(com)

        yield item
