# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.spiders import Spider
from newsCommentCraw.items import newsCommentCrawItem
from scrapy.http import Request
from scrapy.selector import Selector 
import pandas as pd
from os.path import isfile
from time import sleep

class newsCommentCrawSpider(scrapy.Spider):
    name = "newsCommentCraw"
    allowed_domains = ['news.naver.com']
    data = {}
    data['idx'] = 0
    loaded = False
    url = "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&lang=ko&pool=cbox5&objectId="

    def getParams(self, href):
        s = not '?' in href and [] or [ x.split('=') for x in href.split('?')[1].split('&')]
        return { p[0]: p[1] for p in s }

    def load(self):
        self.frame = pd.read_csv('../data/newsTitle.csv')
        if isfile('./checkpoint.json'): 
            with open('./checkpoint.json', 'r') as file:
                self.data = json.load(file)
        print ('data loaded!')
        print (self.data)
        self.loaded = True

    def save(self, idx):
        self.data['idx'] = int(idx)
        with open('./checkpoint.json', 'w') as file:
            json.dump(self.data, file)

    def loop(self):
        if not self.loaded:
            self.load()
        for idx, data in self.frame.iterrows():
            if idx < self.data['idx']: continue
            href = data.href_naver
            if href != href: continue
            params = self.getParams(href)
            yield href, self.url + "news" + params['oid'] + "%2C" + params['aid']
            self.save(idx)

    def start_requests(self):
        for origin, href in self.loop():
            yield Request(href, headers={'Referer': origin}, meta={'origin': origin}, callback = self.parse)
            
    def parse(self, response):
        body = response.body
        res = json.loads(body[10:-2].decode('utf-8'))
        if not res['success']: return
        result = res['result']

        item = newsCommentCrawItem()
        item['href'] = response.meta['origin']
        item['count'] = result['count']['total']
        item['comments'] = []
        columns = ['replyCount', 'modTime', 'contents', 'sympathyCount', 'antipathyCount', 'maskedUserId']
        for comment in result['commentList']:
            com = {}
            for col in columns:
                com[col] = comment[col]
            item['comments'].append(com)
        
        if item['count'] > 0:       
            return item
