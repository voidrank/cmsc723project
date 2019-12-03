import requests
from html.parser import HTMLParser
from IPython import embed
from bs4 import BeautifulSoup
from html2text import html2text
import re
import os
import argparse

'''
def args_parser():
    parser = argparse.ArgumentParser(description='spider for global voices')
    parser.add_argument('author_name', type=str, help='author name')
    return parser


parser = args_parser()

args = parser.parse_args()
author_name = args.author_name
'''


r = requests.get("https://zht.globalvoices.org/for-bloggers/translators/")
soup = BeautifulSoup(r.text)
author_links = list(set(map(lambda e: e['href'], soup.find_all(href=re.compile(".*author.*")))))





class IndexParser(HTMLParser):

    def __init__(self):
        super(IndexParser, self).__init__()
        self._links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            found = False
            for attr in attrs:
                if attr[0] == 'rel' and attr[1] == 'bookmark':
                    found = True
                    break
            if found:
                for attr in attrs:
                    if attr[0] == 'href':
                        self._links.append(attr[1])

for author_link in author_links:
    index_parser = IndexParser()
    r = requests.get(author_link)
    #r = requests.get('https://zht.globalvoices.org/author/{}'.format(author_name))
    index_parser.feed(r.text)
    for i in range(2, 100):
        #r = requests.get('https://zht.globalvoices.org/author/{}/page/{}'.format(author_name, i))
        r = requests.get('{}/page/{}'.format(author_link, i))
        if r.status_code == 200:
            try:
                index_parser.feed(r.text)
            except Exception:
                pass
        else:
            break


    author_name = author_link[author_link[:-1].rfind('/')+1:-1]
    if not os.path.exists(author_name):
        os.mkdir(author_name)

    for idx, href in enumerate(index_parser._links):
        try:
            r = requests.get(href)
            soup = BeautifulSoup(r.text, 'html.parser')
            chinese_text = soup.select('#single')[0]
            chinese_text = html2text(str(chinese_text))
            english_link = soup.find(title=re.compile(".+\ English"))['href']
            r = requests.get(english_link)
            soup = BeautifulSoup(r.text, 'html.parser')
            english_text = soup.select('#single')[0]
            english_text = html2text(str(english_text))
        except Exception:
            continue

        with open("{}/{}_English".format(author_name, idx), 'w') as f:
            f.write(english_text)
        with open("{}/{}_Chinese".format(author_name, idx), 'w') as f:
                f.write(chinese_text)




