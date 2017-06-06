from collections import Counter
import re
from datetime import datetime, timedelta
from string import whitespace
from typing import Union, List
import random
from os import name

POLYGLOT = name == "POSIX"

if POLYGLOT:
    from polyglot.text import Text
from nltk import word_tokenize, pos_tag, ne_chunk
from konlpy.tag import Komoran

from newsCraw.utils.connection import get_exist, get_scroll
from newsCraw.utils.connection import put_bulk, put_item, update_item

def trans_filter(text: str, pattern: dict) -> str:
    """trans_filter filtering text by pattern key to value
    only len(key) == 1
    faster than replace_filter
    just use text_filter
    """
    return text.translate(str.maketrans(pattern))

def replace_filter(text: str, pattern: dict) -> str:
    """replace_filter filtering text by pattern key to value
    slower than trans_filter
    just use text_filter
    """
    for pat, rep in pattern.items():
        text = text.replace(pat, rep)
    return text

def text_filter(text: str, pattern: dict) -> str:
    """text_filter filtering text by pattern key to value
    split pattern trans(len = 1), replace(else) and
    call trans_filter, replace_filter
    """
    tra, rep = {}, {}
    for k, v in pattern.items():
        if len(k) == 1:
            tra[k] = v
        else:
            rep[k] = v
    text = trans_filter(text, tra)
    text = replace_filter(text, rep)
    return text

def tag_filter(text: str) -> str:
    return text_filter(text,
     {"</b>":"", "<b>":"", "</p>":"", "<p>":"",
      "&lt;": "<"})

nullspace = whitespace[1:] + '\xa0'
def whitespace_filter(text: str) -> str:
    return trans_filter(text, {w: ' ' for w in nullspace})

pat_quotations = [
    re.compile("\'(.*?)\'"),
    re.compile('\"(.*?)\"'),
    re.compile('`(.*?)`'),
    re.compile('&#34;(.*?)&#34;'),
    re.compile('\((.*?)\)'),
    re.compile('\{(.*?)\}'),
    re.compile('\[(.*?)\]'),
]

str_quotations = ['\'', '\"', '`', '&#34;', '(', ')', '{', '}', '[', ']']
def quotation_filter(text: str) -> Union[str, List[str]]:
    """return [match_list, filtered_str]
    """
    matches = []
    for pat in pat_quotations:
        for match in pat.finditer(text):
            matches.append(match.groups()[0])
    return matches, text_filter(text, {w: '' for w in str_quotations}).strip()

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
def emoji_filter(text: str):
    return emoji_pattern.sub(r'', text)

def string_filter(text: str):
    text = whitespace_filter(text)
    text = tag_filter(text)
    return quotation_filter(emoji_filter(text))

pat_date_before = re.compile(u'(\d+)(.+?)전')
date_type = ['초', '분', '시간', '일']
def date_filter(date):
    match = pat_date_before.match(date)
    if match:
        date = [0,0,0,0]
        now = datetime.now()
        date[date_type.index(match.group(2))] = int(match.group(1))
        time = now - timedelta(seconds=date[0], minutes=date[1], hours=date[2], days=date[3])
        return str(time)
    return date

def hash(key=32):
    return ''.join([random.choice('0123456789ABCDEF') for _ in range(key)])

def now():
    return str(datetime.now())[:19]

def query_filter(query):
    return ''.join([ '%' + hex(x)[2:] for x in query.encode('euc-kr')])

def parse_param(href):
    s = not '?' in href and [] or [ x.split('=') for x in href.split('?')[1].split('&')]
    return { p[0]: p[1] for p in s }

TAGGER = Komoran()
def extract_entities(text):
    nnps = []
    def put_nnp(nnp):
        pos = TAGGER.pos(nnp)
        temps = []
        for word, tag in pos:
            if tag == 'NNP':
                temps.append(word)
            elif temps:
                nnps.append("".join(temps))
        if temps:
            nnps.append("".join(temps))

    if POLYGLOT:
        polytext = Text(text)
        try:
            for entity in polytext.entities:
                put_nnp(entity[0])
        except:
            pass
            
    for chunk in ne_chunk(pos_tag(word_tokenize(text))):
        if len(chunk) == 1 and chunk.label() == 'ORGANIZATION':
            put_nnp(chunk.leaves()[0][0])
        elif len(chunk)>1 and str(chunk[1]).startswith('NN'):
            put_nnp(chunk[0])

    return set(nnps)

def get_subkey(entity):
    if get_exist(entity, 'entities'):
        return get_scroll({
            '_source': ['subkey'],
            'query': {
                'match': {
                    '_id': entity
                }
            }
        }, index='memento', doc_type='entities')[entity]['subkey']
    put_item({
        'updated': 'false',
        'subkey': [],
        'last_update': now(),
        'related': {
            'entitiy': 0,
            'event': 0,
        }
    }, doc_type='entities', idx=entity)
    return ''


def put_news(items: list, doc_type: str='News_Naver'):
    bulk_items = []
    for item in items:
        item_id = "{}_{}".format(item['oid'], item['aid'])
        need_update = get_exist(item_id, doc_type)

        for entity in item['entities']:
            if not get_exist(entity, 'entities'):
                put_item({
                    'updated': 'false',
                    'subkey': [],
                    'last_update': now(),
                    'related': {
                        'entitiy': 0,
                        'event': 0,
                    }
                }, doc_type='entities', idx=entity)

            if need_update:
                update_item({
                    'inline': 'ctx._source.entities.contains(params.entity) ? (ctx.op = \"none\") : ctx._source.entities.add(params.entity)',
                    'params': {
                        'entity': entity
                    }}, item_id, doc_type=doc_type)

        if not need_update:
            bulk_items.append({
                '_index': 'memento',
                '_type': doc_type,
                '_id': item_id,
                '_source': item
            })

    put_bulk(bulk_items)
