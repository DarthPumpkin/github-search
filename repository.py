import find_sources
import os
import subprocess

def get_target_dir(clone_url):
    splitted_url = clone_url.split('/')
    repo_name = splitted_url[-1]
    repo_name = repo_name.rsplit('.', 1)[0]
    owner = splitted_url[-2]
    return "repos/" + owner + "-" + repo_name

def clone_repo(clone_url):
    if not os.path.exists("repos"):
        os.mkdir("repos")
    
    target_dir = get_target_dir(clone_url)
    if os.path.exists(target_dir):
        return target_dir
        # delete(target_dir)

    subprocess.call(["git", "clone", "--depth", "1", clone_url, target_dir])
    return target_dir

def delete(path):
    for file in os.listdir(path):
        file_path = os.path.join(path,file)
        if os.path.isdir(file_path):
            delete(file_path)
        else:
            os.remove(file_path)
    
    os.rmdir(path)

def java_files(path):
    result = []
    for file in os.listdir(path):
        file_path = os.path.join(path,file)
        if os.path.isdir(file_path):
            sub_dir_java_files = java_files(file_path)
            result.extend(sub_dir_java_files)
        else:
            if file.endswith(".java"):
                result.append(file_path)
    return result

if __name__ == "__main__":
    #find_sources.create_cache()
    urls = find_sources.load_cache()
    print(urls[0])
    target_dir = clone_repo(urls[0])
    print(target_dir)
    java_files = java_files(target_dir)
    print(java_files)
    text = open(java_files[0]).read()
    print(text)
