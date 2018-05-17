# github-search
github-search is a search tool that allows users to search for java functions from popular java repos on GitHub based on keywords and function signature.

Installation
-----
Clone the repo and open a terminal in the repo directory and run 
~~~
#install javalang
pip3 install -e javalang
~~~

Usage
-----
~~~
# Find repositories on github
python3 find_sources.py
# Start elasticsearch in another terminal
# Index everything
python3 main.py

# Search
python3 search.py
> Query: quicksort
> Query: sort ret:int
> Query: read file ret:String[] param:String
~~~

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
Command line interface for the search engine. To search for a function, simply input tags separated by spaces and add a filter by return type by preceding the return type by `ret:`. It is also possible to search for function parameters using the prefix `param:`.

Example
~~~
python3 search.py
Query: sort ret:int[]
....
~~~

License
-------
The code in this repository is distributed under the MIT license. It contains a slightly modified version of [javalang](https://github.com/c2nes/javalang).
