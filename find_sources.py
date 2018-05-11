import requests
import json
import time
import os
import sys
import datetime

green = "\x1b[38;2;0;255;0m"
greenish = "\x1b[38;2;93;173;110m"
red = "\x1b[38;2;255;0;0m"
grey = "\x1b[38;2;193;184;192m"
reset = "\033[0m"
clear_line = "\033[0K"

# Maximum repository size in megabytes
MAX_REPO_SIZE = 5


def load_cache():
    result = []
    for file in os.listdir("sources"):
        if file.endswith(".json"):
            text = open("sources/" + file).read()
            for item in json.loads(text)["items"]:
                size_in_mb = item["size"]/1000
                if size_in_mb > MAX_REPO_SIZE:
                    continue

                result.append(item["clone_url"])

    return list(set(result))


def create_cache():
    print(green + "Searching github..." + reset)
    results = []
    if not os.path.exists("sources"):
        os.mkdir("sources")

    queries = ["utilities", "", "useful", "tools"]
    for query_id, query in enumerate(queries):
        page = 1
        print("\r" + clear_line + "\n" + greenish +
              "Searching using query '{}' (id: {})".format(query, query_id))
        while page < 100:
            path = "sources/query_{}_page_{}.json".format(query_id, page)
            if os.path.exists(path):
                print("\r" + clear_line + green +
                      "Skipping page {}, using data from cache...".format(page) + reset)
                page += 1
                continue
            else:
                print("\r" + clear_line + green +
                      "Searching page {}... ".format(page) + reset, end="")
            r = requests.get(
                "https://api.github.com/search/repositories?q={}+language:java&sort=stars&order=desc&page={}".format(query, page))
            if not r.ok:
                if "Only the first 1000 search results are available" in r.text:
                    print(
                        "limit reached: only the first 1000 search results are available")
                    break
                print(red + "Query failed\n" + r.text + reset)
                print("Sleeping for some time before retrying")
                time.sleep(10)
                continue

            try:
                data = json.loads(r.text)
            except Exception as e:
                print("Json parsing failed")
                print(e)
                print("Sleeping for some time before retrying", end="")
                time.sleep(10)
                continue

            print(green + "done" + reset)
            with open(path, "w") as f:
                f.write(json.dumps(data))

            page += 1
            # Github rate limit of 10 requests per minute
            print(grey + "Sleeping due to rate limit..." + reset, end="")
            sys.stdout.flush()
            time.sleep(60/10)


if __name__ == "__main__":
    create_cache()
    print(load_cache())
