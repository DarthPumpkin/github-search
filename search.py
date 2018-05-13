
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
    print(query.tags)
    print(query.return_type)


if __name__ == "__main__":
    interactive()
