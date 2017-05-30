from datetime import datetime
from typing import Union

from elasticsearch import Elasticsearch

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

def get_scroll(query={}, doc_type='', index='information'):
    array = []
    def _get_scroll(scroll) -> Union[int, list]:
        doc = scroll['hits']['hits']
        array.extend(doc)
        return doc and True or False
    scroll = ES.search(index=index, doc_type=doc_type, body=query, scroll='1m', size=1000)
    scroll_id = scroll['_scroll_id']
    while _get_scroll(scroll):
        scroll = ES.scroll(scroll_id=scroll_id, scroll='1m')
    return make_clear(array)

def get_entities() -> dict:
    return get_scroll({}, 'namugrim')

def get_navernews(date_start, date_end):
    news = get_scroll({
                'query': {
                    'range': {
                        'published_time': {
                            "gte" : date_start,
                            "lte" : date_end,
                            "format": "yyy.MM.dd"
                        }
                    }
                }
            })

    def info_chain(x):
        x['keyword'] = x['information']['keyword']
        x['subkey'] = x['information']['subkey']
        del x['information']
        return x

    return pd.DataFrame(list(map(info_chain, make_clear(news).values())))

def get_type_id(query: list, type: str) -> str:
    wrapper = lambda x: {'match': {x[0]: x[1]}}
    result = ES.search(index='information', doc_type=type, body={
        'query': {
            'bool': {
                'must': list(map(wrapper, query.items()))
            }
        }
    })
    if result['hits']['total']:
        return result['hits']['hits'][0]['_id']
    result = ES.index(
        index='information',
        doc_type=type,
        body=query
    )
    return result['_id']

def put_item(item: dict, type:str, index: str):
    result = ES.index(
        index=index,
        doc_type=type,
        body=item
    )
    print (index, type, result['_id'])
    return result['_id']

# Default Connection Function

def get_daterange():
    return datetime(2000, 1, 1), datetime(2017, 5, 25)
