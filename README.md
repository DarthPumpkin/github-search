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


search.py
---------
Command line interface for the search engine.

Example
~~~
python3 search.py
Query: sort ret:int[]
....
~~~
