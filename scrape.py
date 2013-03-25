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

LOCALWIKI_HOST = os.getenv('LOCALWIKI_HOST', 'http://127.0.0.1:8000')
LOCALWIKI_USERNAME = os.getenv('LOCALWIKI_USERNAME', None)
LOCALWIKI_API_KEY = os.getenv('LOCALWIKI_API_KEY', None)


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
    name = address = phone = website = ''

    entry_content = cached_get_content(TCCL_TOS_HOST + entry_href)
    soup = BeautifulSoup(entry_content)

    name = find_data_by_label(soup, 'Agency Name')
    address = find_data_by_label(soup, 'Address')
    phone = find_data_by_label(soup, 'Phone/Fax')

    linkTable = soup.find('table', 'bibLinks')
    if linkTable:
        website = linkTable.find('a')['href']

    details = get_entry_details(soup)
    print name, address, phone, website
    print details


def find_data_by_label(soup, label):
    tag = soup.find('td', text=label)
    data = tag.find_next_sibling('td', 'bibInfoData').text.strip()
    return data


def get_entry_details(soup):
    details = {}
    detail_table = soup.find_all('table', 'bibDetail')[1]
    for row in detail_table.find_all('tr'):
        label = row.find('td', 'bibInfoLabel')
        data = row.find('td', 'bibInfoData').text.strip()
        if label:
            key = label.text.strip()
            details[key] = [data,]
        else:
            details[key].append(data)
    return details


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


for letter in 'b':
    search_letter(letter)
