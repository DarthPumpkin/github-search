import repository
import indexer
import find_sources
import parse
import javalang

for repo in find_sources.load_cache():
    target_dir = repository.clone_repo(repo)
    for file in repository.java_files(target_dir):
        print("Indexing file " + file)

        try:
            methods = parse.find_methods(open(file).read())
        except javalang.parser.JavaSyntaxError:
            print("Skipping {}, couldn't parse it".format(file))
            continue
        except UnicodeDecodeError:
            print("Skipping {}, couldn't read it as UTF-8".format(file))
            continue
        except KeyboardInterrupt:
            exit(1)
        except Exception as e:
            print("Skipping {}, unknown exception\n{}".format(file, e))
            continue

        print(methods)

