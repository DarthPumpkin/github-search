# github-search

find_sources.py
---------------
Searches github for likely candidates to index.
The results are cached in the `sources` directory. If you delete it the search will be restarted from scratch (which may take a significant amount of time)

- `create_cache()` updates the cache if necessary (delete the `sources` directory to force a full recalculation)
- `load_cache()` returns a list of repo clone URLs from the cache.

Example
~~~
import find_sources
import subprocess

find_sources.create_cache()
urls = find_sources.load_cache()
subprocess.call(["git", "clone", urls[0]])
~~~


repository.py
-------------
Clones the reppsitory and filter it for java files to be passed to the parser.

- `clone_repo()` clones repository into temporary directory before being passed to the java parser.
- `java_files()` filter repository for java files.
- `delete()` deletes repo from the temp folder.
- `get_target_dir()` returns the directory where the repo will be cloned

Example
~~~
import repository
import find_sources

urls = find_sources.load_cache()
for url in urls:
    print('clonning ', url, ' into ', repository.get_target_dir(url))
    target_dir = repository.clone_repo(url)
    java_files = repository.java_files(target_dir)
    print('available java files: ', java_files)
    # parse files and pass to index
    for java_file in java_files:
        text = open(java_file).read()
        print(text)
    repository.delete(target_dir)
~~~

search.py
---------
Command line interface for the search engine.

Example
~~~
python3 search.py
Query: sort ret:int[]
....
~~~

License
-------
The code in this repository is distributed under the MIT license. It contains a slightly modified version of [javalang](https://github.com/c2nes/javalang).
