from urllib.parse import urlsplit
from queue import Queue
import json
import re

from scrapy.selector import Selector

from newsCraw.utils.scrapy_module import Scrapy_Module
from newsCraw.utils.requestable import Requestable, Request
from newsCraw.utils.utility import parse_param, string_filter, date_filter, query_filter, now, put_news, extract_entities

class News_Naver(Scrapy_Module):
    def __init__(self):
        self.allow = ['news.naver.com',
                      'apis.naver.com',
                      'entertain.naver.com',
                      'sports.news.naver.com']
        self.url = "https://search.naver.com/search.naver?where=news&query={}&nso=so%3Ar%2Cp%3Afrom{}to{}%2Ca%3Aall"
        self.crl = "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&lang=ko&pool=cbox5&objectId=news{}%2C{}"
        self.keys = set()
        self.items = Queue()

    def __del__(self):
        items = []
        while not self.items.empty():
            items.append(self.items.get())
        put_news(items)

    @Requestable
    def process_count(self, data: dict) -> Request:
        keyword = data['keyword']
        subkey = data['subkey']
        date = data['date'].replace('-', '')

        key = "{} {}".format(keyword, subkey).strip()
        return Request(self.url.format(query_filter(key), date, date),
                       callback=self.parse_count, meta={
                           'entities': [keyword]
                       })

    def parse_count(self, response):
        def get_count(text):
            count = text.re(r'\/ (.+?)\건')
            count = int(count[0].replace(',', '')) or 0
            return min(count / 10 + 1, 400)
        try:
            count = get_count(Selector(response).xpath('//div[@class="title_desc all_my"]//text()'))
            for page in range(int(count)):
                yield Request(response.url + "&start=" + str(page * 10 + 1), callback=self.parse_title, meta=response.meta)
        except:
            return

    def parse_title(self, response):
        ul = Selector(response).xpath('//ul[@class="type01"]')
        for site in ul.xpath('.//li[contains(@id, "sp_nws")]'):
            item = {'entity': response.meta['entities']}
            item['published_time'] = date_filter(site.xpath('.//dd[@class="txt_inline"]/text()[normalize-space()]').extract_first())
            item['crawled_time'] = now()

            item['href'] = site.xpath('.//a[contains(@class, "_sp_each_title")]//@href').extract_first()
            item['href_naver'] = site.xpath('.//a[contains(@class, "_sp_each_url")]//@href').extract_first()
            if item['href'] != item['href_naver']:
                yield Request(item['href_naver'], callback=self.parse_content, meta={'item': item})
            yield item

    def parse_content(self, response):
        def _get_cate_(selector):
            category = {
                '정치': 'politics',
                '경제': 'economy',
                '사회': 'social',
                '생활/문화': 'life/culture',
                '세계': 'world',
                'IT/과학': 'it/science',
                '오피니언': 'opinion',
                '포토': 'photo',
                'TV': 'tv',
            }
            cate = selector.xpath('//meta[@property="me2:category2"]/@content').extract_first()
            return category[cate] if cate in category else 'news'

        def _get_title_(selector):
            title = selector.xpath('//title//text()').extract_first()
            match = re.search('(.+?) :.+네이버.+$', title)
            if match:
                return match.group(1)
            return title

        def _get_content_(selector):
            contents = ['//div[@id="articleBodyContents"]',
                        '//div[@id="articeBody"]', 
                        '//div[@id="newsEndContents"]']

            text, imgs = [], []
            for content in contents:
                parse = selector.xpath(content)
                text += parse.xpath('.//text()').extract()
                imgs += parse.xpath('.//img/@src').extract()

            skip = lambda x: not x or x.startswith('// flash 오류를 우회하기 위한 함수 추가')

            content = [line for line in map(lambda x: x.strip(), text) if not skip(line)]
            return "\n".join(content), imgs

        item = response.meta['item']

        params = parse_param(response.url)
        item['oid'] = params['oid']
        item['aid'] = params['aid']

        selector = Selector(response)

        category = urlsplit(response.url).netloc.split('.')[0]
        item['cate'] = category if category != 'news' else _get_cate_(selector)

        item['title_quote'], item['title'] = string_filter(_get_title_(selector))

        content, imgs = _get_content_(selector)
        item['imgs'] = imgs
        item['content_quote'], item['content'] = string_filter(content)
        item['entities'] = item['entity'] + extract_entities(item['content'])

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

            if oid == item['oid'] and aid == item['aid']:
                pass

            col_label = ['reply_count', 'mod_time', 'content', 'sympathy_count', 'antipathy_count', 'author']
            col_find = ['replyCount', 'modTime', 'contents', 'sympathyCount', 'antipathyCount', 'maskedUserId']

            for comment in result['commentList']:
                com = {'crawled_time': now()}
                for label, find in zip(col_label, col_find):
                    com[label] = comment[find]

                com['author'] = com['author'] or '***'
                com['mod_time'] = com['mod_time'][:10] + " " + com['mod_time'][11:19]
                com['content_quote'], com['content'] = string_filter(com['content'])

                item['comments'].append(com)

            return self.dress(item)

    def dressor(self, item: dict):
        oid, aid = item['oid'], item['aid']
        if (oid, aid) in self.keys:
            return
        self.keys.add((oid, aid))
        self.items.put(item)
        if self.items.qsize() > 1000:
            items = [self.items.get() for _ in range(1000)]
            put_news(items)
        return item
