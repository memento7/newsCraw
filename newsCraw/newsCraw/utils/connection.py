from datetime import datetime
from typing import Union

from elasticsearch import Elasticsearch
from elasticsearch import helpers
import logging
logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)

import newsCraw.memento_settings as MS
ES = Elasticsearch(**MS.SERVER_ES_INFO)

def make_clear(results: list,
               key_lambda = lambda x: x['_id'],
               value_lambda = lambda x: x,
               filter_lambda = lambda x: x) -> dict:
    def clear(result) -> dict:
        result['_source']['_id'] = result['_id']
        return result['_source']
    iterable = filter(filter_lambda, map(clear, results))
    return {key_lambda(source): value_lambda(source) for source in iterable}

def get_scroll(query={}, doc_type='', index='memento'):
    array = []
    def _get_scroll(scroll):
        doc = scroll['hits']['hits']
        array.extend(doc)
        return doc and True or False
    scroll = ES.search(index=index, doc_type=doc_type, body=query, scroll='1m', size=1000)
    scroll_id = scroll['_scroll_id']
    while _get_scroll(scroll):
        scroll = ES.scroll(scroll_id=scroll_id, scroll='1m')
    return make_clear(array)

def get_entities() -> dict:
    return map(lambda x: (x['keyword'], x['subkey']), 
               get_scroll({"_source": ['keyword', 'subkey']}, doc_type='namugrim').values())

def get_exist(idx: str, doc_type: str, index='memento'):
    return ES.search(
                index=index,
                doc_type=doc_type,
                body = {
                    'query': {
                        'match': {
                            '_id': idx
                        }
                    }
                }
            )['hits']['total']

def update_item(update, idx, doc_type: str, index: str = 'memento'):
        result = ES.update(index=index,
                           doc_type=doc_type,
                           id=idx,
                           body={"script": update})
        return result['_id']

def put_bulk(actions: list):
    helpers.bulk(ES, actions)

def put_item(item: dict, doc_type: str, idx: str = '', index='memento'):
    while True:
        try:
            result = ES.index(
                index=index,
                doc_type=doc_type,
                body=item,
                id=idx
            )
            break
        except: 
            print ('Connection Error wait for 2s')
            sleep(2)
            continue
    return result['_id']
