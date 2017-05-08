from scrapy.selector import Selector

from newsCraw.utils.scrapy_module import Scrapy_Module
from newsCraw.items import newsCrawItem
from newsCraw.utils.requestable import Requestable, Request
from newsCraw.utils.utility import *

from urllib.parse import urlsplit
import json

class News_Naver(Scrapy_Module):
    def __init__(self):
        self.allow = ['news.naver.com', 'apis.naver.com', 'entertain.naver.com', 'sports.news.naver.com']
        self.url = "http://news.naver.com/main/search/search.nhn?query={}&startDate={}&endDate={}"
        self.crl = "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&lang=ko&pool=cbox5&objectId=news{}%2C{}"

    @Requestable
    def process_count(self, keyword, date: str) -> Request:
        key, sub = keyword
        d = date.strftime("%Y-%m-%d")
        return Request(self.url.format(query_filter(key), d, d), callback=self.parse_count, meta={'key': key})

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
                yield Request(item['href_naver'], callback=self.parse_content, meta={'item': item})
            else:
                yield item

    def parse_content(self, response):
        item = response.meta['item']

        params = parse_param(response.url)
        item['oid'] = params['oid']
        item['aid'] = params['aid']

        item['cate'] = urlsplit(response.url).netloc.split('.')[0]

        contents = ['//div[@id="articleBodyContents"]', '//div[@id="articeBody"]', '//div[@id="newsEndContents"]']
        text, imgs = [], []
        for content in contents:
            parse = Selector(response).xpath(content)
            text += parse.xpath('.//text()').extract()
            imgs += parse.xpath('.//img/@src').extract()

        content = []
        for s in text:
            s = s.strip()
            if not len(s): continue
            if s.startswith('// flash 오류를 우회하기 위한 함수 추가'): continue
            content.append(s)

        item['imgs'] = imgs
        item['content_quote'], item['content'] = string_filter("\n".join(content))
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

                if not com['author']: com['author'] = '***'
                com['mod_time'] = com['mod_time'][:10] + " " + com['mod_time'][11:19]
                com['content_quote'], com['content'] = string_filter(com['content'])

                item['comments'].append(com)

            return self.dress(item)

    def dressor(self, tx, item: dict):
        """tx is dbpool object
        # Usage
        - tx.execute(query);
        - tx.fetchone()
        """
        columns = {
            'naver_news': {'href': '%s', 'href_naver': '%s', 'keyword': '%s', 'title': '%s', 'content': '%s', 'published_time': '%s', 'crawled_time': '%s', 'oid': '%d', 'aid': '%d', 'reply_count': '%d', 'cate': '%s', 'hash': '%s'},
            'naver_comment': {'author': '%s', 'content': '%s', 'reply_count': '%d', 'sympathy_count': '%d', 'antipathy_count': '%d', 'mod_time': '%s', 'crawled_time': '%s', 'target': '%d', 'hash': '%s'},
            'naver_quote': {'quote': '%s', 'target': '%d', 'flag': '%d', 'hash': '%s'},
            'naver_img': {'src': '%s', 'target': '%d'},
        }

        def make_query(table, item):
            def decorator(t, text):
                if t == "%d":
                    return int(text)
                else:
                    return '\"{}\"'.format(text)

            keys, values = zip(*columns[table].items())

            q = " INSERT INTO " + table +\
                " ( " + ",".join(keys) + " ) VALUES " +\
                " ( " + ",".join(values) % tuple([decorator(v, item[k]) for k, v in zip(keys, values)]) + " );"
            return q

        def insert_item(table, item, ret=True):
            if ret:
                item['hash'] = hash()
            q = make_query(table, item)

            print (q)
            tx.execute(q)

            if ret:
                tx.execute("SELECT id FROM {} WHERE hash='{}' order by id desc limit 1;".format(
                        table, item['hash']
                    ))
                index = tx.fetchone()
                return index['id']

        """quote_type
            0: title
            1: content
            2: comment
            3: quote
        """
        def put_quotes(quotes: str, target: int, type: int):
            for quote in quotes:
                qlist, quote = quotation_filter(quote)
                if not len(quote): continue
                quote_id = insert_item('naver_quote', {'quote': quote, 'target': target, 'flag': type})
                put_quotes(qlist, quote_id, 3)

        news_id = insert_item('naver_news', item)

        for img in item['imgs']:
            insert_item('naver_img', {'target': news_id, 'src': img}, False)

        for comment in item['comments']:
            comment['target'] = news_id
            comment_id = insert_item('naver_comment', comment)
            put_quotes(comment['content_quote'], comment_id, 2)

        put_quotes(item['title_quote'], news_id, 0)
        put_quotes(item['content_quote'], news_id, 1)
