import indexer
import json

class Query:
    def __init__(self, tags, return_type):
        self.tags = tags
        self.return_type = return_type


def help():
    print("""
Example:
> Query: sort
> Query: sort ret:int
> Query: sort sql where tweets ret:string[]
""")


f = open('config.json')
index_config = json.load(f)


def interactive():

    while True:
        query = input("Query: ").strip()
        if query.lower() in ["help", "?", "commands"]:
            help()
            continue

        parts = query.split()
        tags = []
        ret = None
        for part in parts:
            if ":" in part:
                option, value = part.split(":")
                if option == "ret":
                    ret = value
                else:
                    print("Unknown option '{}'".format(option))
            else:
                tags.append(part)

        search(Query(tags, ret))


def search(query):
    query_dict = {
        "function_score": {
            "query": {
                "multi_match": {
                    "query": " ".join(query.tags),
                    "type": "cross_fields",
                    # "operator": "and",
                    "fields": [
                        "body_tags^3",
                        "inheritance_tags^2",
                        # "import_tags^1",
                        "name_tags^4",
                        "name^4",
                    ]
                }
            },
            "field_value_factor": {
                "field": "score"
            }
        }
    }

    query_dict2 = {
        "match": {
            "body_tags": "json read",
        }
    }

    result = indexer.search(index_config, query_dict)
    print(json.dumps(result, indent=4))

    for hit in result["hits"]["hits"]:
        print(hit["_source"]["body"])
        print()

    # print(query.tags)
    # print(query.return_type)


if __name__ == "__main__":
    interactive()
