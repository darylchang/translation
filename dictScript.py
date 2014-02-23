import urllib2
from bs4 import BeautifulSoup

url = 'https://www.translate.google.com/#es/en/' + 'queda'
headers = {'User-Agent': 'Magic Browser'}
req = urllib2.Request(url, None, headers=headers)
res = urllib2.urlopen(req)
html = res.read()
soup = BeautifulSoup(html)

print soup.prettify()
words = soup.find_all('div', {'class' : 'gt-baf-word-clickable'})