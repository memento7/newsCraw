
# coding: utf-8

# In[102]:

from urllib.parse import unquote, quote
from urllib.request import Request, urlopen, urlretrieve
from bs4 import BeautifulSoup as bs


# In[33]:

import pandas as pd
import pymysql
import requests
import re
import json


# In[34]:

SERVER_RDB = '175.207.13.225'
SERVER_PDB = '175.207.13.224'


# In[196]:

def get_entities():
    conn = pymysql.connect(host=SERVER_PDB,
                           user='memento',
                           password='memento@0x100_',
                           db='memento',
                           charset='utf8')
    cur = conn.cursor()

    columns = ['keyword', 'title', 'content', 'published_time', 'reply_count']

    sql = "SELECT id, realname FROM entity"

    result = cur.execute(sql)
    ret = list(cur)

    cur.close()
    conn.close()

    return ret


# In[202]:

def get_events():
    conn = pymysql.connect(host=SERVER_PDB,
                           user='memento',
                           password='memento@0x100_',
                           db='memento',
                           charset='utf8')
    cur = conn.cursor()

    columns = ['id', 'title']

    sql = "SELECT " + ",".join(columns) + " FROM event"

    result = cur.execute(sql)

    ret = list(cur)

    cur.close()
    conn.close()

    return ret


# In[222]:

def push_event_picture(id, link, w):
    headers = {
        "Content-Type" : "application/json",
        "charset": "utf-8"
    }
    payload = {
        "type": "default",
        "path": link,
        "weight": w
      }
    req = requests.post('http://175.207.13.224:8080/manage/api/persist/events/%d/images' % id, json=[payload], headers=headers)
    res = req.text


# In[223]:

header = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
        'Connection': 'keep-alive'}
def get_picture(query, size=1):
    url = u'https://search.naver.com/search.naver?where=image&query=' + query
    q = Request(quote(url.encode('utf-8'), '/:&?='))
    soup = bs(urlopen(q).read(), 'lxml')
    
    for img in soup.findAll('img', {'class': '_img'})[:3]:
        img_ref = img['data-source']
        if img_ref:
            yield img_ref


# In[221]:

for id, event in get_events():
    for picture in get_picture(event):
        push_event_picture(id, picture, 100)


# In[ ]:

print ('done')


# In[ ]:



