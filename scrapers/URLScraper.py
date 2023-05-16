import threading
import requests
from lxml import etree
import urllib
from bs4 import BeautifulSoup
from tqdm import tqdm

from helpers.CSVHelper import CSVHelper


class URL:
    def __init__(self, dom, item_id):
        self.link = self.get_link(item_id, dom)

    def get_link(self, item_id, dom):
        try:
            elems = dom.xpath(f'//*[@id="searchResults"]/section[{item_id}]/div[4]/div[2]/div[1]/div/a')
            link = elems[0].attrib['href']
            return link
        except:
            return ''


class URLScraper:

    def parse_links(self, search_url, start, end, file_name):
        for page_id in tqdm(range(start, end)):
            tmp_links = []
            url = f"{search_url}&size=100&page={page_id}"
            url = urllib.parse.quote(url, safe='/:?&=')
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            dom = etree.HTML(str(soup))
            for item_id in range(1, 99):
                link = URL(dom, item_id)
                if link.link != '':
                    tmp_links.append(link)
                else:
                    pass
            CSVHelper.write(path=f'./data/cars/{file_name}.csv', data=tmp_links, headers=['links'])


    def threaded_parse_links(self, search_url, num_of_pages, file_name, num_of_threads):
        chunk_size = num_of_pages // num_of_threads
        threads = []
        for i in range(num_of_threads):
            start = 1 + i * chunk_size
            if i != num_of_threads - 1:
                end = start + chunk_size
            else:
                end = 1 + num_of_pages
            thread = threading.Thread(target=self.parse_links, args=(search_url, start, end, file_name))
            threads.append(thread)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

