from pathlib import Path
from rake_nltk import Rake
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
        self.keyword_extractor = Rake()

    def extract_keywords(self, top_n=10, remove_word=None):
        if self._file and not self._text:
            all_text = self._fetch_text_from_file(self._file)
        else:
            all_text = self._text
        self.keyword_extractor.extract_keywords_from_text(all_text)
        top_n_phrases = self.keyword_extractor.get_ranked_phrases()[0:top_n]
        if remove_word:
            remove_word = remove_word.lower()
            top_n_phrases = list(map(lambda x: x.lower().replace(remove_word, ''), top_n_phrases))
        return top_n_phrases

    @staticmethod
    def _fetch_text_from_file(file):
        pattern = r'[.\n]*$'
        with open(file, 'r') as txt_file:
            all_text = '. '.join(map(lambda x: re.sub(pattern, '', x), txt_file.readlines()))
        return all_text
