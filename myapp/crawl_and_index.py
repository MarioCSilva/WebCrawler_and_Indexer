import os
import re
import logging
import requests
# import multiprocessing
import django
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from whoosh import index
from whoosh.fields import Schema, TEXT, NUMERIC
from indexengine.settings import PARSER_STOP_CONTENT, PARSER_STOP_CHARS, PARSER_STOP_WORDS
import django
django.setup()
from myapp.models import Document


logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

# def worker(contents):
#     worker_id = multiprocessing.current_process()._identity[0]

#     schema = Schema(content=TEXT(stored=True))
#     dir_name = f"indexdir_{worker_id-1}"

#     if not index.exists_in(dir_name):
#         os.makedirs(dir_name)
#         ix = index.create_in(dir_name, schema)
#     else:
#         ix = index.open_dir(dir_name)

#     writer = ix.writer()
#     for content in contents:
#         document = Document(content=content)
#         document.save()
#         writer = ix.writer()
#         writer.add_document(content=content)
#         writer.commit()

def crawl_and_index_startup():
    urls = []
    with open("websites_to_crawl.txt", 'r') as urls_file:
        for url in urls_file:
            url = url.strip()
            urls.append(url)

    Crawler(urls).run()

class Crawler:
    def __init__(self, urls=[]):
        self.visited_urls = []
        self.urls_to_visit = urls
        self.max_depth_crawl = 200  # crawl at most 200 urls from a base url
        self.schema = Schema(id=NUMERIC(stored=True, unique=True), content=TEXT(stored=True))
        self.num_workers = 4

    def download_url(self, url, timeout=5):
        session_obj = requests.Session()
        return session_obj.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }, timeout=timeout).text

    def get_linked_urls(self, url, soup):
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
                yield path

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def crawl_and_index(self, url, add_urls, ix):
        html = self.download_url(url)

        soup = BeautifulSoup(html, features="html.parser")

        # Extract scrapped content
        contents = self.extract_contents(soup)

        # Index content
        writer = ix.writer()
        for content in contents:
            try:
                document = Document.objects.get(content=content)
            except Document.DoesNotExist:
                document = None
            if not document:
                document = Document(content=content)
                document.save()
                writer.add_document(id=str(document.id).encode("utf-8").decode("utf-8"), content=content)
        writer.commit()

        # chunk_size = len(contents) // self.num_workers
        # chunks = [contents[i:i + chunk_size] for i in range(0, len(contents), chunk_size)]
        # pool.map(worker, chunks)

        # Add urls to scrape from the same url as base
        if add_urls:
            for i, url in enumerate(self.get_linked_urls(url, soup)):
                self.add_url_to_visit(url)
                if i == self.max_depth_crawl:
                    break

    def extract_contents(self, soup):
        contents = []
        texts = soup.findAll(text=True)
        for text in texts:
            text = text.get_text().strip().replace('\n', ' ').lower()
            # re.sub(r"<[^>]*>", r"", html_content, flags=re.IGNORECASE | re.MULTILINE)
            # Filtering stop chars
            stop_chars_regex = f'(\s)*({"|".join(PARSER_STOP_CHARS)})(\s)*'
            text = re.sub(
                stop_chars_regex, " ", text, flags=re.IGNORECASE | re.MULTILINE
            )
            # Filtering stop words
            stop_words_regex = f'(\s)+({"|".join(PARSER_STOP_WORDS)})(\s)+'
            text = re.sub(
                stop_words_regex, " ", text, flags=re.IGNORECASE | re.MULTILINE
            )
            # Removing all numbers, except years
            text = re.sub(r"(\s)+(?!((19[0-9]{2}|20[0-9]{2})))([0-9]+)(\s)+",
                          r" ", text, flags=re.IGNORECASE | re.MULTILINE,
                          )
            # Replacing multiple spaces by only one
            text = re.sub("(\s)+", " ", text).strip()
 
            # Ignoring empty text and
            # text that contains the content in the stop content
            # and text that contains less than 5 words
            if text\
                and not any(content in text for content in PARSER_STOP_CONTENT)\
                and len(text.split(' ')) > 5:
                contents.append(text)
        # Removing duplicates
        contents = list(set(contents))
        return contents

    def run(self):
        len_initial_url = len(self.urls_to_visit)
        total_crawled_urls = 0
        # pool = multiprocessing.Pool(processes=self.num_workers)

        if not index.exists_in("indexdir"):
            os.makedirs("indexdir")
            ix = index.create_in("indexdir", self.schema)
        else:
            ix = index.open_dir("indexdir")

        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)
            logging.info(f'Crawling: {url}')
            try:
                self.crawl_and_index(url, True if total_crawled_urls <
                           len_initial_url else False, ix)
                total_crawled_urls += 1
            except Exception:
                logging.exception(f'Failed to crawl: {url}')
            finally:
                self.visited_urls.append(url)

        # pool.close()
        # pool.join()
        # The merge_indexes function does not exist
        # whoosh.merge_indexes("indexdir", [f"indexdir/{i}" for i in range(self.num_workers)])


