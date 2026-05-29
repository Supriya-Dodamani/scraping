import os
import requests
from bs4 import BeautifulSoup

os.chdir(r'c:\Users\Supriya M Dodamani\OneDrive\Desktop\scraoing\college_scraper_agent')
ua = UserAgent()
for url in [
    'https://www.shiksha.com/university-college/colleges/mba-colleges-in-bengaluru',
    'https://collegedunia.com/mba-colleges-in-bengaluru'
]:
    print('URL:', url)
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    resp = requests.get(url, headers=headers, timeout=20)
    print(' status', resp.status_code)
    print(' length', len(resp.text))
    print(' snippet', resp.text[:400].replace('\n',' '))
    soup = BeautifulSoup(resp.text, 'lxml')
    print(' total anchors', len(soup.select('a[href]')))
    print(' selected /university-college/', len(soup.select("a[href*='/university-college/']")))
    print(' selected /college/', len(soup.select("a[href*='/college/']")))
    print('--- sample ---')
    count = 0
    for a in soup.select('a[href]'):
        href = a.get('href', '')
        if '/university-college/' in href or '/college/' in href:
            print(href)
            count += 1
            if count >= 20:
                break
    print('--- done ---\n')

import time
from fake_useragent import UserAgent
from urllib.parse import quote_plus

query = 'colleges in Bengaluru offering MBA MCA BCA site:shiksha.com'
ua = UserAgent()
headers = {'User-Agent': ua.random, 'Accept-Language': 'en-US,en;q=0.9'}
url = f'https://www.google.com/search?q={quote_plus(query)}&num=10'
print('Google search URL:', url)
resp = requests.get(url, headers=headers, timeout=20)
print('Google status', resp.status_code)
soup = BeautifulSoup(resp.text, 'lxml')
print('Google total anchors', len(soup.select('a[href]')))
for i, a in enumerate(soup.select('a[href]')):
    href = a['href']
    print(i, href)
    if i >= 30:
        break
