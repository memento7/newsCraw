# -*- coding: utf-8 -*-

from scrapy import signals
from scrapy.utils.project import get_project_settings
from twisted.enterprise import adbapi
import pymysql
import re
import sys

SETTINGS = get_project_settings()

pat_rl = [re.compile('\\n'), re.compile('\\t')]
pat_dl = [re.compile('\n\/\/')]

def dl_filter(content):
    ret = False
    for pat in pat_dl:
        ret = ret or pat.match(content)
    return ret

def content_filter(content):
    content = ''.join([ cont for cont in content if not dl_filter(cont) ])
    for pat in pat_rl:
        content = re.sub(pat, '', content)
    return content.replace("\"", "")

def title_filter(title):
    return title.replace("\"", "")

class newsCrawPipeline(object):

    def __init__(self):
        #Instantiate DB
        self.dbpool = adbapi.ConnectionPool ('pymysql',
            host = SETTINGS['DB_HOST'],
            user = SETTINGS['DB_USER'],
            passwd = SETTINGS['DB_PASSWD'],
            port = SETTINGS['DB_PORT'],
            db = SETTINGS['DB_DB'],
            charset = 'utf8',
            cursorclass = pymysql.cursors.DictCursor
        )
        self.col = {}
        self.col['Articles'] = SETTINGS['DB_ARTICLES_COLUMNS'].split(',')
        self.col['Articles_int'] = SETTINGS['DB_ARTICLES_COLUMNS_INT'].split(',')
        self.col['Comments'] = SETTINGS['DB_COMMENTS_COLUMNS'].split(',')
        self.col['Comments_int'] = SETTINGS['DB_COMMENTS_COLUMNS_INT'].split(',')

        query = self.dbpool.runInteraction(self.set_names)
        query.addErrback(self.q_error)

    def set_names(self, tx):
        result = tx.execute('SET NAMES utf8')
        result |= tx.execute('SET CHARACTER SET utf8')
        result |= tx.execute('SET character_set_connection=utf8')
        print (result)

    def open_spider(self, spider):
        conn = pymysql.connect(
            host=SETTINGS['QDB_HOST'],
            port=SETTINGS['QDB_PORT'],
            user=SETTINGS['QDB_USER'],
            passwd=SETTINGS['QDB_PASSWD'],
            db=SETTINGS['QDB_DB'],
            charset='utf8')
        cur = conn.cursor()
        cur.execute('select realname from entity')

        spider.keywords = [ name[0] for name in cur ]

        cur.close()
        conn.close()

    def close_spider(self, spider):
        self.dbpool.close()
        print('done!!!')

    def process_item(self, item, spider):
        item['title'] = title_filter(item['title'])
        item['content'] = content_filter(item['content'])

        query = self.dbpool.runInteraction(self.q_insert_article, item)
        query.addErrback(self.q_error)

        if 'comments' in item:
            for comment in item['comments']:
                query = self.dbpool.runInteraction(self.q_insert_comment, comment)
                query.addErrback(self.q_error)

        return item

    def q_insert_article(self, tx, item):
        q = "INSERT INTO Articles " +\
            "(" + ",".join(self.col['Articles'] + self.col['Articles_int']) + ")" +\
            " VALUES (%s,%s,%s,%s,%s,%s,%s,%d,%d,%d)" % (\
            tuple([ '\"' + item[col] +'\"' for col in self.col['Articles'] ]) +\
            tuple([ int(item[col]) for col in self.col['Articles_int'] ]) )
        
        result = tx.execute(q)

    def q_insert_comment(self, tx, item):
        q = "INSERT INTO Comments " +\
            "(" + ",".join(self.col['Comments'] + self.col['Comments_int']) + ")" +\
            " VALUES (%s,%s,%s,%s,%d,%d,%d)" % (\
            tuple([ '\"' + item[col] +'\"' for col in self.col['Comments'] ]) +\
            tuple([ int(item[col]) for col in self.col['Comments_int'] ]) )

        result = tx.execute(q)

    def q_error(self, e):
        print(e)