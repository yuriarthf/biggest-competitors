import requests
import re
from pathlib import Path
from .custom_exceptions import BadReturnCode, InvalidArgument
from bs4 import BeautifulSoup, Comment


class Spider:
    def __init__(self, initial_url=None):
        self.initial_url = initial_url

    def get_url(self, url=None):
        if url is None:
            url = self.initial_url
        r = requests.get(url)
        if r.status_code != 200:
            raise BadReturnCode(r.status_code)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup

    @staticmethod
    def get_website_name(website):
        pattern = r'(?:(?:http|https)://w{0,3}\.?)(\w+)(?:\..*)'
        website_name = re.match(pattern, website).group(1)
        return website_name

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
        return f'{sep}'.join(urn)

    def get_output_path_and_folder(self, url, rel_output_folder='output'):
        company_name = self.get_website_name(url)
        full_output_folder = Path(rel_output_folder) / company_name
        full_output_folder.mkdir(parents=True, exist_ok=True)
        full_output_path_html = full_output_folder / (self.get_urn(url, sep='.') + '.html')
        full_output_path_txt = full_output_folder / (self.get_urn(url, sep='.') + '.txt')
        return full_output_path_html, full_output_path_txt, full_output_folder, company_name

    @staticmethod
    def save_html_to_folder(html, full_output_path_html):
        with open(full_output_path_html, 'w') as html_file:
            html_file.writelines(str(html.prettify()))

    def save_text_content_to_folder(self, html, blacklist_elem, full_output_path_txt, filter_non_ascii=True):
        self._remove_all_comment_tags(html)
        all_text = [t.strip(' ') for t in html.find_all(text=True)
                    if t.parent.name not in blacklist_elem]
        all_text = filter(lambda x: x != '' and x != 'html', map(self.remove_trailing_leading_spaces, all_text))
        if filter_non_ascii:
            all_text = map(self.filter_non_ascii, all_text)
        with open(full_output_path_txt, 'w') as txt_file:
            txt_file.write('\n'.join(all_text))

    @staticmethod
    def _remove_all_comment_tags(soup):
        comments = soup.find_all(text=lambda x: isinstance(x, Comment))
        [comment.extract() for comment in comments]

    @staticmethod
    def filter_non_ascii(text):
        text = text.encode('ascii', 'ignore').decode()
        return text

    @staticmethod
    def remove_trailing_leading_spaces(text):
        pattern = r'(^[\n\t\r\s]*|[\n\t\r\s]*$)'
        text = re.sub(pattern, '', text)
        return text

    @staticmethod
    def _add_www_if_necessary(website):
        website_split_protocol = website.split('//')
        if website_split_protocol[1].split('.')[0] != 'www':
            website_split_protocol[1] = 'www.' + website_split_protocol[1]
        return '//'.join(website_split_protocol)

    def _replace_http_for_https(self, website, add_www=True):
        https_website = website.replace('http', 'https')
        if not https_website.endswith('/'):
            https_website += '/'
        if add_www:
            https_website = self._add_www_if_necessary(https_website)
        return https_website

    def _replace_https_for_http(self, website, add_www=True):
        http_website = website.replace('https', 'http')
        if not http_website.endswith('/'):
            http_website += '/'
        if add_www:
            http_website = self._add_www_if_necessary(http_website)
        return http_website

    def _get_href_from_anchors(self, url, soup, https_or_http='http', same_uri=True):
        if https_or_http not in ['http', 'https']:
            raise InvalidArgument('https_or_http argument must have a value of \'http\' or \'https\'')
        refs = list()
        pattern = r'(http|https)://.+'
        for a in soup.find_all('a', href=True):
            ref = a['href']
            if re.match(pattern, ref):
                refs.append(ref)
        if https_or_http == 'http':
            normalized_url = self._replace_https_for_http(url)
            normalized_refs = map(lambda x: self._replace_https_for_http(x), refs)
        else:
            normalized_url = self._replace_http_for_https(url)
            normalized_refs = map(lambda x: self._replace_http_for_https(x), refs)
        normalized_refs = filter(lambda x: x != normalized_url, normalized_refs)
        if same_uri:
            normalized_refs = filter(lambda x: normalized_url in x, normalized_refs)
        return list(normalized_refs)

    def recursive_get_html(self, recursive_urls=2, initial_url=None, save_text=True):
        if initial_url is None:
            initial_url = self.initial_url
        urls = [initial_url]
        company_name, path_to_folder = None, None
        for i in range(recursive_urls):
            new_urls = list()
            for url in urls:
                full_output_path_html, full_output_path_txt, full_output_folder, company_name = (
                    self.get_output_path_and_folder(url, rel_output_folder='output'))
                if full_output_path_html.is_file() and full_output_path_html.is_file():
                    continue
                html = self.get_url(url)
                if full_output_path_html.is_file():
                    continue
                self.save_html_to_folder(html, full_output_path_html)
                if save_text and not full_output_path_txt.is_file():
                    self.save_text_content_to_folder(html, ['script', 'style'], full_output_path_txt)
                if i < recursive_urls - 1:
                    new_urls.extend(self._get_href_from_anchors(url, html))
            urls = list(set(new_urls))
        return company_name, path_to_folder
