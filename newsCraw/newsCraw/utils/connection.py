from elasticsearch import Elasticsearch
from datetime import datetime

ES = Elasticsearch([{
    'host': 'server2.memento.live', 
    'port': 9200
}])

def make_clear(results,
               key_lambda = lambda x: x['_id'],
               value_lambda = lambda x: x,
               filter_lambda = lambda x: x):
    def clear(result):
        result['_source']['_id'] = result['_id']
        return result['_source']
    iterable = filter(filter_lambda, map(clear, results))
    return {key_lambda(source): value_lambda(source) for source in iterable}

def get_keywords():
    def _get_scroll_(scroll):
        scroll_doc = scroll['hits']['hits']
        return len(scroll_doc), scroll_doc
    keywords = []
    scroll = ES.search(index='information', doc_type='namugrim', scroll='1m', size=1000)
    scroll_id = scroll['_scroll_id']
    scrolled, scroll_doc = _get_scroll_(scroll)
    keywords.extend(scroll_doc)
    while scrolled:
        scroll = ES.scroll(scroll_id=scroll_id, scroll='1m')
        scrolled, scroll_doc = _get_scroll_(scroll)
        keywords.extend(scroll_doc)
    return make_clear(keywords)

def get_daterange():
    return datetime(2000, 1, 1), datetime(2017, 5, 25)

def get_type_id(info: dict, module: str) -> str:

    def put_key(subkey):
        result = ES.index(
            index='information',
            doc_type=module,
            body={
                'keyword': info['keyword'],
                'subkey': subkey
            }
        )
        return result['_id']

    def _get_type_id(result, subkey):
        if subkey in result:
            return result[subkey]
        return put_key(subkey)

    try:
        result = ES.search(index='information', doc_type=module, body={
            'query': {
                'match': {
                    'keyword': info['keyword'],
                }
            }
        })
        result = make_clear(result['hits']['hits'], 
                            lambda x: x['subkey'],
                            lambda x: x['_id'],
                            lambda x: x['subkey'] in info['subkeys'])
    except:
        result = {}

    return {subkey: _get_type_id(result, subkey) for subkey in info['subkeys']}

def put_item(item: dict, type: str, index: str):
    result = ES.index(
        index=index,
        doc_type=type,
        body=item
    )
    return result['_id']
