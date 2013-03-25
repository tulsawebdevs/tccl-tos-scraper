import hashlib
import os
import time

from bs4 import BeautifulSoup
import requests


TCCL_TOS_HOST = 'http://opac.tulsalibrary.org:82'
TCCL_TOS_PATH = 'search~S0'
TCCL_TOS_PARAMS = {
    'searchtype': 't',
    'searcharg': '',
    'SORT': 'D',
    'extended': 0,
    'SUBMIT': 'Search',
    'searchlimits': '',
    'searchorigarg': 'ta'
}


def search_letter(letter):
    search_params = TCCL_TOS_PARAMS.copy()
    search_params['searcharg'] = letter
    print "POST"
    resp = requests.post('%s/%s' % (TCCL_TOS_HOST, TCCL_TOS_PATH),
                         data=search_params)
    soup = BeautifulSoup(resp.content)
    scrape_entries(soup)


def scrape_entries(soup):
    entries = soup.find_all('td', 'browseEntryData')
    for entry in entries:
        entry_link = entry.find_all('a')[1]
        copy_entry(entry_link['href'])
    next_link = soup.find('a', text='Next')
    if next_link:
        next_content = cached_get_content(TCCL_TOS_HOST + next_link['href'])
        next_soup = BeautifulSoup(next_content)
        scrape_entries(next_soup)


def copy_entry(entry_href):
    pass


def cached_get_content(url, cache_timeout=3600):
    path_hash = hashlib.md5(url).hexdigest()
    cache_file = 'cache/%s' % path_hash

    content = None
    if os.path.exists(cache_file) and file_age(cache_file) < cache_timeout:
        content = open(cache_file, 'r').read()

    if not content:
        print "GET"
        resp = requests.get(url)
        content = resp.content
        open(cache_file, 'w').write(content)

    return content


def file_age(fn):
    return time.time() - os.stat(fn).st_mtime


for letter in 'ab':
    search_letter(letter)
