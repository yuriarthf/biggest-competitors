from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from crawler.spider import Spider
from keyword_extractor.extractor import Keyword_Extractor
from search_engine.search import SearchQueryList
from crawler.custom_exceptions import BadReturnCode
from geolite2 import geolite2
import re
import socket
import sys

app = Flask(__name__)
api = Api(app)


def clean_list_of_elem(list_, elem_):
    while True:
        try:
            list_.remove(elem_)
        except ValueError:
            break


def get_queries_from_folder(path_to_folder):
    queries = list()
    for f in path_to_folder.iterdir():
        if f.is_file() and f.suffix == '.html':
            kw_extractor = Keyword_Extractor(f)
            queries.extend(map(lambda kw: ' '.join(kw), kw_extractor.extract_top_keywords().values()))
    clean_list_of_elem(queries, '')
    return queries


def get_country_code(url):
    pattern_http = r'^(http|https)://'
    pattern_urn = r'/.*$'
    url = re.sub(pattern_urn, '', re.sub(pattern_http, '', url))
    if not url.startswith('www.'):
        url = 'www.' + url
    try:
        ip = socket.gethostbyname(url)
    except socket.gaierror:
        return None
    reader = geolite2.reader()
    country_code = reader.get(ip)['country']['iso_code']
    geolite2.close()
    return country_code


class Competitors(Resource):
    def post(self):
        posted_data = request.form
        initial_url = posted_data['company_url']
        spider = Spider(initial_url)
        try:
            company_name, path_to_folder = spider.recursive_get_html()
        except BadReturnCode as e:
            return jsonify(({
                'status': e.status_code,
                'message': e.message
            }))
        queries = get_queries_from_folder(path_to_folder)
        search_instance = SearchQueryList(queries)
        country_code = get_country_code(initial_url)
        most_common_websites = search_instance.get_top_n_pages(
            remove_pages_with_word=company_name, country=country_code)
        most_common_websites = list(map(lambda elem: elem[0], most_common_websites))
        return jsonify({
            'status': 200,
            'top_competitors': most_common_websites
        })


api.add_resource(Competitors, '/competitors')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
