import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as hcluster
import scipy.cluster.vq as vq

import pymysql
import requests
import re
import json

from datetime import datetime, timedelta
from collections import defaultdict

SERVER_RDB = '175.207.13.225'
SERVER_PDB = '175.207.13.224'

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
    ret = [ c[:2] for c in cur]

    cur.close()
    conn.close()

    return ret

def get_data(qs, qe):
    conn = pymysql.connect(host=SERVER_RDB,
                           user='memento',
                           password='memento@0x100_',
                           db='memento',
                           charset='utf8')
    cur = conn.cursor()

    columns = ['keyword', 'title', 'content', 'published_time', 'reply_count', 'href_naver']

    sql = "SELECT " + ",".join(columns) + " FROM articles where published_time between \'" +\
            qs + "\' and \'" + qe +"\'"

    result = cur.execute(sql)

    frame = pd.DataFrame(list(cur), columns=columns)
    max_len = max(frame.content.apply(lambda x : len(x)))
    frame['per'] = frame.content.apply(lambda x : int(round(max_len / (len(x) + 1))))

    cur.close()
    conn.close()

    return frame

# find quotation for 'important word'
pat_small_quot = re.compile(u"\'(.+?)\'")
pat_double_quot = re.compile(u"\"(.+?)\"")
def find_quotation(text):
    mat_small = pat_small_quot.finditer(text)
    mat_double = pat_double_quot.finditer(text)
    return list(mat_small) + list(mat_double)

# use Twitter Tagger
from konlpy.tag import Twitter
tagger = Twitter()
def tokenize(text):
    return tagger.morphs(text)

stop_words = []
def tokenize_stop(text, stop=stop_words):
    return [ token for token in tokenize(text) if token not in stop ]

pos_tags = ['Noun']
neg_tags = ['KoreanParticle', 'PreEomi', 'Punctuation', 'Eomi', 'Number', 'Foreign', 'URL']
def stemize_pos(text, tags=pos_tags):
    return [ word for word, tag in tagger.pos(text) if tag in tags]

def stemize_neg(text, tags=neg_tags):
    return [ word for word, tag in tagger.pos(text) if not tag in tags]

def tagging(text, neg_tags=[]):
    return [ "{}/{}".format(word, tag) for word, tag in tagger.pos(text) if not tag in neg_tags]

zip_tags = ['Noun', 'Alpha']
token_key = '**//*//**//**/*/**//*//**/**'
def stemize_tagging(text, zip_tags=zip_tags, neg_tags=neg_tags):
    match_str = []
    c = 0
    for match in find_quotation(text):
        text = text[:match.start() + c] + " " + token_key + " " + text[match.end() + c:]
        c += len(token_key) - len(match.group()) + 2
        match_str.append(match.group()[1:-1])
    ret = []
    for tokens in [ tagger.pos(word) for word in text.split() ]:
        if len(tokens) < 2:
            ret.append(tokens[0][0])
            continue
        zipper = []
        for word, pos in tokens:
            if pos in zip_tags: 
                zipper.append(word)
            else:
                if zipper: ret.append("".join(zipper))
                if pos not in neg_tags: ret.append(word)
                zipper[:] = []
        if zipper: ret.append("".join(zipper))
    return [ r == token_key and match_str.pop() or r for r in ret ]

def time_range(date, pat, day=10):
    dates = []
    for d in range(day):
        delta = timedelta(days=d)
        dates.append((date + delta).strftime("%Y-%m-%d"))
        dates.append((date - delta).strftime("%Y-%m-%d"))
    return dates

def parser(row):
    content = stemize_tagging(row.content)
    title = stemize_tagging(row.title)
    date = time_range(row.published_time.to_pydatetime(), "%Y-%m-%d")
    keyword = row.keyword
    return title, content, date, keyword

from gensim.models import Doc2Vec
from gensim.models.doc2vec import LabeledSentence

rate_content = 1
rate_title = 10
rate_date = 5
rate_keyword = 25

class LabeledLineSentence(object):
    def __init__(self, frame):
        self.frame = frame
        self.s = []
        for idx, row in self.frame.iterrows():
            title, content, date, keyword = parser(row)
            self.s.append({'title':title,'content':content,'date':date,'keyword':keyword,'per':row.per})
    
    def lines(self):
        ret = []
        for idx, s in enumerate(self.s):
            ret.append(LabeledSentence(s['content'] + s['title'] + s['date'] + [s['keyword']], ['line_%s' % idx]))
        return ret
    
    def __iter__(self):
        for idx, s in enumerate(self.s):
            l = len(s['content'])
            q = s['title']*int(l/int(100/rate_title))+                s['content']+                s['date']*int(l/int(100/rate_date))+                [s['keyword']]*int(l/int(100/rate_keyword))
            yield LabeledSentence(q, ['line_%s' % idx])

def get_topic(frame):
    iframe = frame[frame['title'].str.contains(keyword)]
    if iframe.empty:
        return frame.reply_count.argmax()
    else:
        return iframe.reply_count.argmax()

def get_keywords(titles, contents):
    title_tag = stemize_pos(" ".join(titles))
    content_tag = stemize_pos(" ".join(contents))
    dic = defaultdict(int)
    for tag in title_tag + content_tag:
        dic[tag] += 1
    tags = sorted([(k, v) for k, v in dic.items()], key=lambda x: -x[1])
    return tags

def get_memento_rate(frame):
    replys = frame.reply_count.sum()
    r, c = frame.shape
    return int(r * 100 + replys)


# pipelines
def pipeline_article(eid, title, href, cc):
    headers = {
        "Content-Type" : "application/json",
        "charset": "utf-8"
    }
    payload = {
      "comment_count": cc,
      "crawl_target": "NAVERNEWS",
      "source_url": href,
      "summary": "",
      "title": title
    }
    req = requests.post('http://175.207.13.224:8080/manage/api/persist/events/' + str(eid) + '/articles', json=payload, headers=headers)
    res = req.text

def pipeline_realtion(kid, eids):
    headers = {
        "Content-Type" : "application/json",
        "charset": "utf-8"
    }
    for eid in eids:
        req = requests.post('http://175.207.13.224:8080/manage/api/persist/entities/' + str(kid) + '/events/' + str(eid))
        res = req.text

def pipeline_event(title, date, keywords, rate, articles):
    headers = {
        "Content-Type" : "application/json",
        "charset": "utf-8"
    }
    payload = {
        "date" : date + " 00:00:00",
        "title" : title,
        "type" : '연예',
        "status" : 0,
        "issue_score" : rate,
        "emotions" : [],
        "keywords" : [ {"keyword": k, "weight": v} for k, v in keywords],
        "summaries" : []
        }
    req = requests.post('http://175.207.13.224:8080/manage/api/persist/events', json=payload, headers=headers)
    res = json.loads(req.text)
    id = res['id']

    for idx, article in articles.iterrows():
        title = article.title
        href = article.href_naver
        cc = article.reply_count
        pipeline_article(id, title, href, cc )
    return id

thresh = 12

date_start = datetime(2016,7,14)
date_end = datetime(2016,12,31)
date_range = timedelta(days=30)
date_jump = timedelta(days=15)

entities = get_entities()
for day in range(int((date_end - date_start) / date_jump)):
    date_s = date_start + date_jump * day
    date_e = date_s + date_range
    print ('date range', date_s, date_e)

    df = get_data(date_s.strftime("%Y/%m/%d"), date_e.strftime("%Y/%m/%d"))

    for keyword in np.unique(df.keyword.values):
        kid = 0
        for k, entity in entities:
            if keyword == entity:
                kid = k
                break
        print ('start with keyword', keyword)

        key_frame = df.loc[df.keyword == keyword]
        r, c = key_frame.shape
        if r < thresh: continue
        print ('there are', r, 'news')

        sentences = LabeledLineSentence(key_frame)

        model = Doc2Vec(alpha=0.025, min_alpha=0.025, window=5)
        model.build_vocab(sentences.lines())

        for epoch in range(11):
            model.train(sentences)
            model.alpha *= 0.98
            model.min_alpha = model.alpha

        clusters = hcluster.fclusterdata(model.docvecs, thresh, criterion="distance")

        key_frame = key_frame.assign(cluster = clusters)

        eid = []
        print ('news cluster: ', len(np.unique(clusters)))
        for cluster in np.unique(clusters):
            i_frame = key_frame.loc[key_frame.cluster == cluster]
            r, c = i_frame.shape
            if (r < thresh / 2): continue
            print (cluster, 'has', r)
            memento_rate = get_memento_rate(i_frame)
            keywords = get_keywords(i_frame.title.values, i_frame.content.values)
            topic = i_frame.ix[get_topic(i_frame)]
            title = topic.title
            date = str(topic.published_time)[:10]

            related = [ keyword for keyword in keywords if keyword in entities ]
            eid.append(pipeline_event(title, date, keywords[:10], memento_rate, i_frame))
        pipeline_realtion(kid, eid)
