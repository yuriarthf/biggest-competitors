from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from crawler.spider import Spider
from keyword_extractor.extractor import Keyword_Extractor
from search_engine.search import SearchQueryList
from crawler.custom_exceptions import BadReturnCode

app = Flask(__name__)
api = Api(app)


def clean_list_from_elem(list_, elem_):
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
    clean_list_from_elem(queries, '')
    return queries


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
        most_common_websites = search_instance.get_top_n_pages(remove_pages_with_word=company_name)
        most_common_websites = list(map(lambda elem: elem[0], most_common_websites))
        return jsonify({
            'status': 200,
            'top_competitors': most_common_websites
        })


api.add_resource(Competitors, '/competitors')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
