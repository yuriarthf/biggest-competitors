from googleapi import google
from collections import Counter


class SearchPages:
    def __init__(self, query):
        self.query = query

    def get_top_n_pages(self, num_pages=4):
        search_results = google.search(self.query, num_pages)
        search_results = map(lambda x: x.link, search_results)
        return search_results


class SearchQueryList:
    def __init__(self, query_list, pages_per_query=4):
        self.query_list = query_list
        self.pages_per_query = pages_per_query

    def get_top_n_pages(self, top_n_pages=5, remove_pages_with_word=None):
        url_counter = Counter()
        for query in self.query_list:
            search_results = SearchPages(query) \
                .get_top_n_pages(self.pages_per_query)
            if remove_pages_with_word:
                search_results = filter(lambda url: remove_pages_with_word not in url, search_results)
            url_counter.update(search_results)
        return url_counter.most_common(top_n_pages)
