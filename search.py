import indexer
import json

class Query:
    def __init__(self, tags, return_type, parameter):
        self.tags = tags
        self.return_type = return_type
        self.parameter = parameter


def help():
    print("""
Example:
> Query: sort
> Query: sort ret:int
> Query: sort sql where tweets ret:string[]
""")

green = "\x1b[38;2;0;255;0m"
greenish = "\x1b[38;2;93;173;110m"
red = "\x1b[38;2;255;0;0m"
grey = "\x1b[38;2;193;184;192m"
reset = "\033[0m"
clear_line = "\033[0K"

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
        parameter = None
        show_json = False
        show_response = False
        for part in parts:
            if ":" in part:
                option, value = part.split(":")
                if option == "ret":
                    ret = value
                elif option == "param":
                    parameter = value
                elif option == "show" and value == "response":
                    show_response = True
                else:
                    print("Unknown option '{}'".format(option))
            else:
                tags.append(part)
        search(Query(tags, ret, parameter), show_response)

def search(query, show_response = False):
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
                        "name^5",
                    ]
                }
            },
            "functions": [{
                "field_value_factor": {
                    "field": "score"
                }
            }],
        }
    }

    if query.return_type is not None:
        if query.return_type == "void":
            query.return_type = "null"
        query_dict["function_score"]["functions"].append({ "filter": { "match": { "return_type": query.return_type }}, "weight": 10})

    if query.parameter is not None:
        query_dict["function_score"]["functions"].append({ "filter": { "match": { "parameters.type": query.parameter }}, "weight": 10})

    result = indexer.search(index_config, query_dict)

    if show_response:
        print("Response:")
        print(json.dumps(result, indent=4))
        print()
        print()
        print()

    print(green + "Found " + str(len(result["hits"]["hits"])) + " function(s)" + reset)
    print()
    for i, hit in enumerate(result["hits"]["hits"]):
        print(green + str(i+1) + ":" + reset)
        source = hit["_source"]
        retType = source["return_type"]
        if retType == "null":
            retType = "void"

        print(retType + " " + source["name"] + "(" + ", ".join([p["type"] + " " + p["name"] for p in source["parameters"]]) + ")", end="")

        print(fix_indentation_in_body(source["body"]))
        print()

    # print(query.tags)
    # print(query.return_type)

def fix_indentation_in_body(body_str):
    lines = body_str.splitlines()

    # find min indentation
    min_indent = 100000
    for line in lines[1:]:
        indent = 0
        for i in range(len(line)):
            if line[i] != ' ' and line[i] != '\t':
                indent = i
                break
        if indent < min_indent and indent != len(line):
            min_indent = indent

    fixed_body = lines[0] + '\n'
    for line in lines[1:]:
        fixed_body += line[min_indent:] + '\n'
    return fixed_body

if __name__ == "__main__":
    interactive()
