
# coding: utf-8

# In[ ]:

import pandas as pd
import pymysql
import re
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import numpy
import scipy.cluster.hierarchy as hcluster
import scipy.cluster.vq as vq
from collections import defaultdict, Counter
import itertools


# In[ ]:

SERVER_RDB = '175.207.13.225'
columns = ['id', 'title', 'content']
def get_data(columns):
    conn = pymysql.connect(host=SERVER_RDB,
                           user='memento',
                           password='memento@0x100_',
                           db='memento',
                           charset='utf8')
    cur = conn.cursor()
    sql = "SELECT " + ",".join(columns) + " FROM articles"
    result = cur.execute(sql)
    result = list(cur)
    cur.close()
    conn.close()
    return result


# In[ ]:

def put_init():
    conn = pymysql.connect(host=SERVER_RDB,
                           user='memento',
                           password='memento@0x100_',
                           db='memento',
                           charset='utf8')
    return conn, conn.cursor()


# In[ ]:

def put_data(cur, columns, data):
    cols = ",".join(["{}=\"{}\"".format(col, content[col]) for col in columns[1:]])
    sql = "UPDATE articles SET {} WHERE id={}".format(cols, data['id']) 
    result = cur.execute(sql)


# In[ ]:

def put_commit(conn):
    conn.commit()


# In[ ]:

def put_final(conn, cur):
    cur.close()
    conn.close()


# In[ ]:

frame = pd.DataFrame(get_data(columns), columns=columns)


# In[ ]:

stopwords = ['◇', '◆', '○', '...', '△', '=', '<', '&lt;', '>', '&gt;', '&nbsp;', '<b>', '</b>', '<span>', '<i>', '</i>'] 


# In[ ]:

def remove_stops(content):
    for stop in stopwords:
        content = content.replace(stop, '')
    return content


# In[ ]:

conn, cur = put_init()


# In[ ]:

h, w = frame.shape
for idx, content in frame.iterrows():
    if not idx % 1000 and idx: 
        print (idx, '/' , h)
    content.title = remove_stops(content.title).strip()
    content.content = remove_stops(content.content).strip()
    put_data(cur, columns, content)


# In[ ]:

put_commit(conn)
put_final(conn, cur)


# In[ ]:



