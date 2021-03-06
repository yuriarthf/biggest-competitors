from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from collections import Counter
import re

CSE_ID = '3b5ce016690d198d5'
API_KEY = 'AIzaSyAdcwsaDv3UZoA1X8wy8rkILUE9GHi1pR4'


class SearchPages:
    def __init__(self, query):
        self.query = query

    @staticmethod
    def _add_www_if_necessary(website):
        website_split_protocol = website.split('//')
        if website_split_protocol[1].split('.')[0] != 'www':
            website_split_protocol[1] = 'www.' + website_split_protocol[1]
        return '//'.join(website_split_protocol)

    def _replace_https_for_http(self, website, add_www=True):
        http_website = website.replace('https', 'http')
        if not http_website.endswith('/'):
            http_website += '/'
        if add_www:
            http_website = self._add_www_if_necessary(http_website)
        return http_website

    @staticmethod
    def get_urn(website, sep='/'):
        pattern = r'(http|https)://'
        website_without_http = re.sub(pattern, '', website)
        urn = website_without_http.split('/')[1:]
        try:
            urn.remove('')
        except ValueError:
            pass
        if not urn:
            return 'index'
        urn = f'{sep}'.join(urn)
        return urn

    def remove_urn(self, website):
        pattern = r'/*$'
        urn = self.get_urn(website.rstrip('/'))
        url = re.sub(pattern, '', website.replace(urn, ''))
        return url

    def standardize_website(self, website):
        standardized_website = self._replace_https_for_http(website)
        standardized_website = self.remove_urn(standardized_website)
        return standardized_website

    @staticmethod
    def google_search(search_term, api_key, cse_id, **kwargs):
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
        try:
            items = res['items']
        except KeyError:
            items = []
        return items

    def get_top_n_pages(self, num_pages=20, standardize_website=True):
        try:
            search_results = self.google_search(self.query, API_KEY, CSE_ID, num=num_pages)
        except HttpError:
            return list()
        search_results = map(lambda res: res['link'], search_results)
        if standardize_website:
            search_results = map(self.standardize_website, search_results)
        return list(search_results)


class SearchQueryList:
    def __init__(self, query_list, pages_per_query=4):
        self.query_list = query_list
        self.pages_per_query = pages_per_query

    def get_top_n_pages(self, top_n_pages=10, remove_pages_with_word=None):
        url_counter = Counter()
        for query in self.query_list:
            search_results = SearchPages(query) \
                .get_top_n_pages(self.pages_per_query)
            if remove_pages_with_word:
                search_results = filter(lambda url: remove_pages_with_word not in url, search_results)
            url_counter.update(search_results)
        n_most_common_websites = url_counter.most_common(top_n_pages)
        return n_most_common_websites
