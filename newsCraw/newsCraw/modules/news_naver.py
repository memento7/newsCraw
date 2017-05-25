from urllib.parse import urlsplit
import json
import re

from scrapy.selector import Selector

from newsCraw.utils.scrapy_module import Scrapy_Module
from newsCraw.utils.requestable import Requestable, Request
from newsCraw.utils.utility import parse_param, string_filter, date_filter, query_filter, now

class News_Naver(Scrapy_Module):
    def __init__(self):
        self.allow = ['news.naver.com',
                      'apis.naver.com',
                      'entertain.naver.com',
                      'sports.news.naver.com']
        self.url = "http://news.naver.com/main/search/search.nhn?query={}&startDate={}&endDate={}"
        self.crl = "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&lang=ko&pool=cbox5&objectId=news{}%2C{}"
        self.keys = set()
        
    @Requestable
    def process_count(self, data: dict) -> Request:
        self.keyword = data['keyword']
        self.subkey = data['subkey']
        self.date = data['date'].strftime("%Y-%m-%d")

        key = self.keyword + " " + self.subkey
        return Request(self.url.format(query_filter(key), self.date, self.date),
                       callback=self.parse_count, meta={
                           'key': key,
                           'keyword': self.keyword,
                           'subkey': self.subkey,
                           'date': self.date
                       })

    def parse_count(self, response):
        def get_count(text):
            count = text.re(r'\/ (.+?)\건')
            count = int(count[0].replace(',', '')) or 0
            return min(count / 10 + 1, 400)
        try:
            count = get_count(Selector(response).xpath('//span[@class="result_num"]/text()'))
            for page in range(int(count)):
                yield Request(response.url + "&page=" + str(page), callback=self.parse_title, meta=response.meta)
        except:
            return

    def parse_title(self, response):
        for site in Selector(response).xpath('//ul[@class="srch_lst"]'):
            item = {
                'information': response.meta
            }
            item['published_time'] = date_filter(site.xpath('.//span[@class="time"]//text()').extract_first())
            item['crawled_time'] = now()
            item['href'] = site.xpath('.//a[@class="tit"]//@href').extract_first()
            item['href_naver'] = site.xpath('.//a[@class="go_naver"]//@href').extract_first()

            if item['href_naver']:
                yield Request(item['href_naver'], callback=self.parse_content, meta={'item': item})
            yield item

    def parse_content(self, response):
        def _get_cate_(selector):
            return selector.xpath('//meta[@property="me2:category2"]/@content').extract_first()

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
        key = item['href_naver']
        if key in self.keys:
            return
        self.keys.add(key)
        return item
