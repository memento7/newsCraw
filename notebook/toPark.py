
# coding: utf-8

# ## Query data

# In[1]:

import pandas as pd
import pymysql


# In[ ]:

conn = pymysql.connect(host='localhost',
                       user='memento',
                       password='memento@0x100_',
                       db='memento',
                       charset='utf8')
cur = conn.cursor()


# In[ ]:

sql = "SELECT * FROM Articles where keyword like '김태희'"


# In[ ]:

result = cur.execute(sql)


# In[ ]:

db_data = []
for c in cur:
    db_data.append(c)


# In[ ]:

s = ['index', 'href', 'href_origin', 'keyword', 'title', 'content', 'ptime', 'ctime', 'oid', 'aid', 'rec']


# In[ ]:

frame = pd.DataFrame(db_data, columns=s)


# In[ ]:

cur.close()
conn.close()


# ## Tokenize

# In[ ]:

from konlpy.tag import Twitter
tagger = Twitter()

def tokenize(text):
    return tagger.morphs(text)

pos_tags = ['Noun']
def stemize_pos(text):
    return [ word for word, tag in tagger.pos(text) if tag in pos_tags]


# ## save

# In[ ]:

from datetime import datetime, timedelta

with open('../data/kim.txt', 'w') as f:
    for idx, content in frame.iterrows():
        text = " ".join(stemize_pos(content.content))
        title = " ".join(stemize_pos(content.title))
        dates = []
        date_origin = datetime.strptime(content.ptime.strftime('%Y-%m-%d')[:10], "%Y-%m-%d")
        for idx in range(10):
            for _ in range(12-idx):
                dates.append(date_origin + timedelta(days=idx))
                dates.append(date_origin + timedelta(days=-idx))
        date = " ".join([ date.strftime("%Y%m%d") for date in dates ])
        f.write(text * 1 + title * int(len(text)/5) + date * int(len(text)/20) + "\n")

