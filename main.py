import repository
import indexer
import find_sources
import parse
import javalang
import json
from tqdm import tqdm
from progressbar import progressbar

f = open('config.json')
index_config = json.load(f)

if not indexer.elastic_search_is_running(index_config):
    print('Elastic search is not responding on ' + index_config['host'] + ':' + index_config['port'])
else:
    indexer.delete_index(index_config)

    if not indexer.index_exists(index_config):
        print('Index \"' + index_config['index'] +'\" was not found')
        print('Creating index \"' + index_config['index'] + '\"')
        indexer.create_index(index_config)


urls = find_sources.load_cache()[0:50]
for repo in tqdm(urls):

    target_dir = repository.clone_repo(repo)
    for file in repository.java_files(target_dir):
        # print("Indexing file " + file)

        try:
            methods = parse.find_methods(open(file).read())
        except javalang.parser.JavaSyntaxError:
            # print("Skipping {}, couldn't parse it".format(file))
            continue
        except UnicodeDecodeError:
            # print("Skipping {}, couldn't read it as UTF-8".format(file))
            continue
        except KeyboardInterrupt:
            exit(1)
        except Exception as e:
            # print("Skipping {}, unknown exception\n{}".format(file, e))
            continue

        # print(methods)
        for method in methods:
            indexer.insert_function(index_config, method)
