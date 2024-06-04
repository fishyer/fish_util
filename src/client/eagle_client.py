import requests
import json
from fish_util.src.yaml_util import YamlLoader
from fish_util.src.log_util import FishLogger

logger = FishLogger(__file__)
print = logger.debug


# 有则返回folder对象，无则创建文件夹并返回folder对象
def get_folder(folder_name):
    folder = get_folder_by_name(folder_name)
    if folder is None:
        folder = create_folder(folder_name)
    return folder


# get folder by name
def get_folder_by_name(folder_name):
    url = "http://localhost:41595/api/folder/list"
    payload = {}
    headers = {
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Accept": "*/*",
        "Host": "localhost:41595",
        "Connection": "keep-alive",
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    json_data = json.loads(response.text)
    json_list = json_data["data"]
    return find_folder_by_name(json_list, folder_name)


def find_folder_by_name(json_list, folder_name):
    for folder in json_list:
        # print(folder["name"])
        if folder["name"] == folder_name:
            return folder
        if "children" in folder:
            find = find_folder_by_name(folder["children"], folder_name)
            if find is not None:
                return find
    return None


# Create a new folder
def create_folder(folder_name):
    url = "http://localhost:41595/api/folder/create"
    payload = json.dumps({"folderName": folder_name})
    headers = {
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Host": "localhost:41595",
        "Connection": "keep-alive",
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # 返回json数据的data.id
    return response.json()["data"]


# Create a new sub folder
def create_sub_folder(parent_id, folder_name):
    url = "http://localhost:41595/api/folder/create"
    payload = json.dumps({"folderName": folder_name, "parent": parent_id})
    headers = {
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Host": "localhost:41595",
        "Connection": "keep-alive",
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # 返回json数据的data.id
    return response.json()["data"]


def add_item_with_cache(image_url, source, folder_id, file_name):
    if check_eagle_cache(image_url):
        # print("cache hit")
        return
    else:
        add_item(image_url, source, folder_id, file_name)
        caches["iamge_urls"].append(image_url)
        yml.file_dump(caches)


# 添加到Eagle库的MarkSearch文件夹: LW8LECFYUG93K
def add_item(image_url, source, folder_id, file_name):
    url = "http://localhost:41595/api/item/addFromURLs"
    payload = json.dumps(
        {
            "items": [
                {
                    "url": image_url,
                    "website": source,
                    "name": file_name,
                }
            ],
            "folderId": folder_id,
        }
    )
    headers = {
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Host": "localhost:41595",
        "Connection": "keep-alive",
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)
    return response.json()


cache_file = "/Users/yutianran/Documents/MyCode/fish_script/cache/eagle.yaml"
yml = YamlLoader(cache_file)
caches = yml.file_load()
image_urls = caches["iamge_urls"]


def check_eagle_cache(image_url):
    if image_url in image_urls:
        return True
    else:
        return False


def test_add_tjd():
    # 专辑 https://www.sqmuying.com/a/?id=72179
    # 图片 https://tjqew5fe8ew.lt508.com/5eb7a_kmt72179-fc2ce-01.jpg
    # https://tjqew5fe8ew.lt508.com/5eb7a_kmt72179-fc2ce-04.jpg
    # https://tjqew5fe8ew.lt508.com/5eb7a_kmt72179-fc2ce-082.jpg
    # https://tjqew5fe8ew.lt508.com/1zfca_okc52288-01.jpg
    zj_id = 65763
    zj_count = 83
    # https://tjqew5fe8ew.lt508.com/4d68f_na65763/cover.jpg
    # https://tjqew5fe8ew.lt508.com/4rgaz_sla65763-01.jpg
    zj_folder_id = get_folder(str(zj_id))["id"]
    print(f"zj_folder_id: {zj_folder_id}")
    zj_url = f"https://www.sqmuying.com/a/?id={zj_id}"
    for i in range(1, zj_count + 1):
        image_url = f"https://tjqew5fe8ew.lt508.com/4rgaz_sla{zj_id}-0{i}.jpg"
        print(image_url)
        image_item = add_item(image_url, zj_url, zj_folder_id, f"{zj_id}-{i}")


def main():
    print(__file__)
    test_sub_id = get_folder_by_name("test-sub")["id"]
    print(test_sub_id)


if __name__ == "__main__":
    main()
