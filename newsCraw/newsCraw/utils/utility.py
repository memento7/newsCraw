from datetime import datetime, timedelta
import re

pat_rl = [re.compile('\\n'), re.compile('\\t')]
pat_dl = [re.compile('\n\/\/')]
pat_da = re.compile(u'(\d+)(.+?)전')
date_type = ['초', '분', '시간', '일']

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

def date_checker(date):
    return pat_da.match(date)

def date_now():
    return datetime.now()
    
def date_filter(date):
    match = pat_da.match(date)
    if match:
        date = [0,0,0,0]
        now = date_now()
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
