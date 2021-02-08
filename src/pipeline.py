import json

from biothings.utils.web.es_dsl import AsyncSearch
from biothings.web.pipeline import ESQueryBuilder


class SmartAPIQueryBuilder(ESQueryBuilder):

    def default_string_query(self, q, options):

        search = AsyncSearch()

        if q == '__all__':
            search = search.query()

        elif q == '__any__' and self.allow_random_query:
            search = search.query('function_score', random_score={})

        else:  # override
            query = {
                "query": {
                    "dis_max": {
                        "queries": [
                            {"term": {"info.title": {"value": q, "boost": 2.0}}},
                            {"term": {"server.url": {"value": q, "boost": 1.1}}},
                            {"term": {"_id": q}},
                            {"query_string": {"query": q}},
                            {"query_string": {"query": q + "*", "boost": 0.8}}
                        ]
                    }
                }
            }
            search = AsyncSearch()
            search = search.update_from_dict(query)

        search = search.params(rest_total_hits_as_int=True)
        search = search.source(exclude=['_raw'])

        if options.authors:  # '"Chunlei Wu"'
            search = search.filter('terms', info__contact__name__raw=options.authors)

        if options.tags:  # '"chemical", "drug"'
            search = search.filter('terms', tags__name__raw=options.tags)

        return search