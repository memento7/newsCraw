from datetime import datetime, timedelta
from string import whitespace
import re

from typing import Union, List

def text_filter(text: str, pattern: List[str]) -> str:
    for pat in pattern:
        text = text.replace(pat, "")
    return text

def tag_filter(text: str) -> str:
    return text_filter(text, ["</b>", "<b>", "</p>", "<p>"])

def char_filter(text: str, pattern: dict) -> str:
    return text.translate(str.maketrans(pattern))

nullspace = whitespace[1:] + '\xa0'
def whitespace_filter(text: str) -> str:
    return char_filter(text, {w: None for w in nullspace})

pat_squote = re.compile("\'(.*?)\'")
pat_dquote = re.compile('\"(.*?)\"')
pat_pbracket = re.compile('\((.*?)\)')
pat_cbracket = re.compile('\{(.*?)\}')
pat_sbracket = re.compile('\[(.*?)\]')
pat_quotations = [pat_squote, pat_dquote, pat_pbracket, pat_cbracket, pat_sbracket]
str_quotations = ['\'', '\"', '(', ')', '{', '}', '[', ']']
def quotation_filter(text: str) -> Union[str, List[str]]:
    """return [match_list, filtered_str]
    """
    matches = []
    for pat in pat_quotations:
        for match in pat.finditer(text):
            matches.append(match.groups()[0])
    return matches, char_filter(text, {w: None for w in str_quotations}).strip()

def string_filter(text: str):
    text = whitespace_filter(text)
    text = tag_filter(text)
    return quotation_filter(text)

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

def now():
    return str(datetime.now())

def query_filter(query):
    return ''.join([ '%' + hex(x)[2:] for x in query.encode('euc-kr')])

def parse_param(href):
    s = not '?' in href and [] or [ x.split('=') for x in href.split('?')[1].split('&')]
    return { p[0]: p[1] for p in s }
