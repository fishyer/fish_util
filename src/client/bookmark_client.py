from bookmarks_converter import BookmarksConverter
from pathlib import Path
import arrow
import shutil
import json
from pathlib import Path
from fish_util.src.log_util import print


def read_json(filepath):
    with open(filepath, "r", encoding="Utf-8") as file_:
        jsondata = json.load(file_)
    return jsondata


def print_info(other_folder):
    other_count = len(other_folder)
    print(f"Found {other_count} bookmarks in the Other Bookmarks folder.")
    for i in range(other_count):
        item = other_folder[i]
        item_type = item.get("type")
        name = item.get("name")
        url = item.get("url")
        if item_type == "url" and name and url:
            print(f"  {i+1}. {name} {url}")
        elif item_type == "folder" and name:
            print(f"  {i+1}. subfolder: {name}")
        else:
            print(f"  {i+1}. warning: invalid bookmark: {item}")


def get_bookmarks():
    # 复制Chrome书签的json文件到cache目录
    db_path = (
        "/Users/yutianran/Library/Application Support/Google/Chrome/Default/Bookmarks"
    )
    source_file = Path(db_path)
    destination_folder = Path("cache/bookmark")
    now = arrow.now()
    now_str = now.format("YYYYMMDD_HHmmss")
    file_path = now_str + "_" + str(source_file.name)
    destination_file = destination_folder / file_path
    shutil.copy(source_file, destination_file)
    # print(f"Copied {source_file} to {destination_file}")

    # 标准化json文件
    output_file = Path(destination_file).with_name("temporary.json")
    BookmarksConverter.format_json_file(destination_file, output_file)
    # print(f"Converted {destination_file} to {output_file}")

    # 解析json文件
    json_data = read_json(output_file)
    bar_folder = json_data.get("children")[0].get("children")
    other_folder = json_data.get("children")[1].get("children")
    # assert json_data.get("name") == "root"
    # assert json_data.get("children")[0].get("name") == "书签栏"
    # assert json_data.get("children")[1].get("name") == "Other Bookmarks"
    # bar_count = len(bar_folder)
    # print(f"Found {bar_count} bookmarks in the Bookmarks bar,")
    # for i in range(bar_count):
    # print(f"  {i+1}. {bar_folder[i].get('name')}")
    # print_info(other_folder)
    print(f"bar_folder: {len(bar_folder)}, other_folder: {len(other_folder)}")
    return bar_folder, other_folder


def get_links_from_folder(other_folder):
    link_list = []
    title_set = set()
    url_set = set()
    for item in other_folder:
        item_type = item.get("type")
        name = item.get("name")
        url = item.get("url")
        if item_type == "url" and name not in title_set and url not in url_set:
            link_list.append({"title": name, "url": url})
            title_set.add(name)
            url_set.add(url)
        else:
            print(f"    Skipping invalid item: {item}")
    print(f"Found {len(link_list)} links in the Bookmarks folder.")
    return link_list


def main():
    print(__file__)
    bar_folder, other_folder = get_bookmarks()
    print(f"bar_folder: {len(bar_folder)}, other_folder: {len(other_folder)}")


if __name__ == "__main__":
    main()
