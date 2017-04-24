from scrapy.selector import Selector

from newsCraw.utils.scrapy_module import Scrapy_Module
from newsCraw.items import newsCrawItem
from newsCraw.utils.requestable import Requestable, Request
from newsCraw.utils.utility import *

import json

class News_Naver(Scrapy_Module):
    def __init__(self):
        self.allow = ['news.naver.com', 'apis.naver.com', 'entertain.naver.com', 'sports.news.naver.com']
        self.url = "http://news.naver.com/main/search/search.nhn?query={}&startDate={}&endDate={}"
        self.crl = "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&lang=ko&pool=cbox5&objectId=news{}%2C{}"

    @Requestable
    def process_count(self, keyword: str, date: str) -> Request:
        d = date.strftime("%Y-%m-%d")
        return Request(self.url.format(query_filter(keyword), d, d), callback=self.parse_count, meta={'key': keyword})

    def parse_count(self, response):
        def get_count(text):
            count = text.re(r'\/ (.+?)\건')
            count = int(count[0].replace(',', '')) or 0
            return min(count / 10 + 1, 400)
        try:
            count = get_count(Selector(response).xpath('//span[@class="result_num"]/text()'))
            key = response.meta['key']
            for page in range(int(count)):
                yield Request(response.url + "&page=" + str(page), callback=self.parse_title, meta={'key': key})
        except:
            return
    def parse_title(self, response):
        for site in Selector(response).xpath('//ul[@class="srch_lst"]'):
            item = {}
            item['keyword'] = response.meta['key']
            item['title_quote'], item['title'] = string_filter(site.xpath('.//a[@class="tit"]').re(r'\>(.+?)\<\/a')[0])
            item['published_time'] = date_filter(site.xpath('.//span[@class="time"]//text()').extract_first())
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

        item['content_quote'], item['content'] = string_filter(" ".join(news_naver + entertain + sports))
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

                com['mod_time'] = com['mod_time'][:10] + " " + com['mod_time'][11:19]
                com['content_quote'], com['conotent'] = string_filter(com['content'])

                item['comments'].append(com)

            return self.dress(item)

    def dressor(self, tx, item):
        news_columns = {'href': '%s', 'href_naver': '%s', 'keyword': '%s', 'title': '%s', 'content': '%s', 'published_time': '%s', 'crawled_time': '%s', 'oid': '%d', 'aid': '%d', 'reply_count': '%d'}
        comment_columns = {'author': '%s', 'content': '%s', 'reply_count': '%d', 'sympathy_count': '%d', 'antipathy_count': '%d', 'mod_time': '%s', 'crawled_time': '%s', 'target': '%d'}
        quote_columns = {'quote': '%s', 'target': '%d', 'flag': '%d'}
        def get_last_id():
            q = "SELECT LAST_INSERT_ID()";
            r = tx.execute(q);
            index = tx.fetchone()['LAST_INSERT_ID()']
            return index

        def make_query(table, columns, item):
            def decorator(t, text):
                if t == "%d":
                    return int(text)
                else:
                    return '\"{}\"'.format(text)

            keys, values = zip(*columns.items())
            q = " INSERT INTO " + table +\
                " ( " + ",".join(keys) + " ) VALUES " +\
                " ( " + ",".join(values) % tuple([decorator(v, item[k]) for k, v in zip(keys, values)]) + " );"
            return q

        q = make_query('naver_news', news_columns, item)
        r = tx.execute(q)
        news_id = get_last_id()

        for comment in item['comments']:
            comment['target'] = news_id
            q = make_query('naver_comments', comment_columns, comment)
            r = tx.execute(q)

            comment_id = get_last_id()
            for quote in comment['content_quote']:
                q = make_query('naver_quote', quote_columns, {'quote': quote, 'target': comment_id, 'flag': 2})
                r = tx.execute(q)

        for quote in item['title_quote']:
            q = make_query('naver_quote', quote_columns, {'quote': quote, 'target': news_id, 'flag': 0})
            r = tx.execute(q)

        for quote in item['content_quote']:
            q = make_query('naver_quote', quote_columns, {'quote': quote, 'target': news_id, 'flag': 1})
            r = tx.execute(q)
