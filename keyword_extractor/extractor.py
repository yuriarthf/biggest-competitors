from pathlib import Path
from bs4 import BeautifulSoup
from gensim.summarization import keywords
import re


class Keyword_Extractor:
    def __init__(self, file_or_text):
        if not isinstance(file_or_text, Path):
            path_to_file = Path(file_or_text)
        else:
            path_to_file = file_or_text
        if path_to_file.is_file():
            self._file = path_to_file
            self._text = None
        else:
            self._text = file_or_text
            self._file = None

    def _load_html_text_from_file(self):
        with open(self._file, 'r') as html_file:
            html_text = ''.join(html_file.readlines())
        return html_text

    @staticmethod
    def extract_keywords_from_text(text, number_of_keywords=5, exclude_elem=None):
        keyword_set = set(keywords(text, words=number_of_keywords, split=True))
        keyword_set.discard(exclude_elem)
        return keyword_set

    @staticmethod
    def _clean_text(text):
        pattern_begin = r'^[\n\s\t\r]*'
        pattern_end = r'[\n\s\t\r]*$'
        new_text = re.sub(pattern_end, '', re.sub(pattern_begin, '', text))
        return new_text

    def _get_meta_with_name(self, soup, name):
        try:
            meta = self._clean_text(soup.find(attrs={'name': name})['content'])
        except TypeError:
            meta = ''
        return meta

    def _get_heading_tags(self, soup, max_heading_level=1):
        heading_text = list()
        for i in range(1, max_heading_level+1):
            try:
                heading_text.append(self._clean_text(soup.find(f'h{i}').text))
            except AttributeError:
                pass
        return heading_text

    def _get_keywords_from_headings(self, heading_list, exclude_keyword=None):
        heading_keywords = set()
        for heading in heading_list:
            heading_keywords.update(self.extract_keywords_from_text(heading))
        heading_keywords.discard(exclude_keyword)
        return heading_keywords

    def extract_top_keywords(self, exclude_keyword=None):
        if self._file:
            html_text = self._load_html_text_from_file()
        else:
            html_text = self._text
        soup = BeautifulSoup(html_text, 'html.parser')
        title = self._clean_text(soup.find('title').text)
        description = self._get_meta_with_name(soup, 'description')
        keywords_meta = self._get_meta_with_name(soup, 'keywords')
        # heading_text = self._get_heading_tags(soup)
        keywords_meta = set(keywords_meta.split(','))
        keywords_meta.discard(exclude_keyword)
        keyword_dict = {
            'title': self.extract_keywords_from_text(title, exclude_elem=exclude_keyword),
            'description': self.extract_keywords_from_text(description, exclude_elem=exclude_keyword),
            'keywords_meta': keywords_meta,
            # 'heading_text': self._get_keywords_from_headings(heading_text, exclude_keyword=exclude_keyword)
        }
        return keyword_dict
