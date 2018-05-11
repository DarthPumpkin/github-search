import requests
import json

def elastic_search_is_running(index_config):
    request_url = 'http://' + index_config['host'] + ':' + index_config['port'] + '/_cat/indices?v'
    try:
        r = requests.get(request_url, timeout=1)
    except requests.exceptions.RequestException as e:  # This is the correct syntax    return False
        return False
    return True

def index_exists(index_config):
    request_url = 'http://' + index_config['host'] + ':' + index_config['port'] + '/' + index_config['index'] + '/'
    r = requests.head(request_url)
    if r.status_code == 200:
        return True
    return False

def create_index(index_config):
    settings_dict = {'number_of_shards': 1, 'number_of_replicas': 1}
    index_dict = {'settings': settings_dict}
    index_json_str = json.dumps(index_dict)
    headers = {'Content-Type': 'application/json'}
    request_url = 'http://' + index_config['host'] + ':' + index_config['port'] + '/' + index_config['index'] + '/'
    r = requests.put(request_url, data = index_json_str, headers = headers)

def delete_index(index_config):
    request_url = 'http://' + index_config['host'] + ':' + index_config['port'] + '/' + index_config['index'] + '/'
    r = requests.delete(request_url)

# Should probably contain some information on where to find the function (repo, file name, line number)
def insert_function(index_config, function_name, return_type, arguments, keywords):
    function_dict = {'name': function_name, 'return_type': return_type, 'arguments': arguments, keywords: keywords}
    function_json_str = json.dumps(function_dict)
    headers = {'Content-Type': 'application/json'}
    request_url = 'http://' + index_config['host'] + ':' + index_config['port'] + '/' + index_config['index'] + '/function/'
    r = requests.post(request_url, data = function_json_str, headers = headers)

if __name__ == "__main__":
    f = open('config.json')
    index_config = json.load(f)

    if elastic_search_is_running(index_config) == False:
        print('Elastic search is not responding on ' + index_config['host'] + ':' + index_config['port'])
    else:
        if index_exists(index_config) != True:
            print('Index \"' + index_config['index'] +'\" was not found')
            print('Creating index \"' + index_config['index'] + '\"')
            create_index(index_config)


            insert_function(index_config, 'max', 'int', ['int', 'int'], ['max'])
