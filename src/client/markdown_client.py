import re
import fish_util.src.time_util as time_util
import fish_util.src.file_util as file_util
from fish_util.src.log_util import print
import arrow
import pathlib
import frontmatter
import fish_util.src.client.dida_client
import time
from fish_util.src.client.dida_client import DidaTask


black_list = ["https://marker.dotalk.cn/"]


def parse_links_from_mdfile(file_path):
    link_list = []
    title_set = set()
    url_set = set()
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        links = re.findall(r"(?<!\!)\[(.*?)\]\((.*?)\)", content)
        for title, url in links:
            if (
                check_url_validity(url)
                and url not in url_set
                and title not in title_set
            ):
                link_list.append({"title": title, "url": url})
                title_set.add(title)
                url_set.add(url)
            else:
                pass
                # print(f"    Skipping invalid url: {url}")
    print(f"Found {len(link_list)} links in {file_path}")
    return link_list


def check_url_validity(url):
    for i in black_list:
        if url.startswith(i):
            return False
    return True


def create_file_from_links(link_list, output_file_path):
    with open(output_file_path, "w", encoding="utf-8") as file:
        for link in link_list:
            file.write(f"- [{link['title']}]({link['url']} )\n")
    print(f"{len(link_list)} Links Created: {output_file_path}")


def get_frontmatter_properties(content):
    post = frontmatter.loads(content)
    frontmatter_properties = {
        "id": post["id"],
        "title": post["title"],
        "url_source": post["url_source"],
    }
    return frontmatter_properties


ob_vault = "MyNote"
access_token = "3ad46d12-a0d6-454d-8ccc-e3bbce0aa943"
inbox_project_id = "inbox1010592152"
archive_project_id = "664cc4c1a20203c5258687e7"


def check_cache(link, inbox_tasks: list[DidaTask]):
    task_title = f"[{link['title'].strip()}]({link['url'].strip()})"
    for task in inbox_tasks:
        if task.title == task_title:
            return True
        if task.title == link["title"]:
            return True
        if task.title == link["url"]:
            return True
    return False


def main():
    print(__file__)
    # mdpath = "/Users/yutianran/Documents/MyNote/dida/Xarray，一个牛逼的python库.md"
    # content = file_util.read_file(mdpath)
    # fp = get_frontmatter_properties(content)
    # print(fp)
    # note_dir = time_util.get_time_dir("test")
    dir_path = "/Users/yutianran/Documents/MyNote/daily/2024/05"
    inbox_tasks = dida_client.get_project_by_id(access_token, inbox_project_id)
    archive_tasks = dida_client.get_project_by_id(access_token, archive_project_id)
    if inbox_tasks is None or archive_tasks is None:
        print("Failed to get inbox or archive tasks")
        return
    print(f"Inbox Tasks: {len(inbox_tasks)}")
    print(f"Archive Tasks: {len(archive_tasks)}")
    # 遍历dir_path下的所有md文件
    for file_path in pathlib.Path(dir_path).glob("*.md"):
        print(file_path)
        # file_path = "/Users/yutianran/Documents/MyNote/daily/2024/05/2024-05-18.md"
        parsed_links = parse_links_from_mdfile(file_path)

        for i, link in enumerate(parsed_links):
            task_name = f"[{link['title'].strip()}]({link['url'].strip()})"
            print(f"Processing Link {i+1}/{len(parsed_links)}: {task_name}")
            if check_cache(link, inbox_tasks):
                print(f"    Skipping {task_name} as it is already in inbox")
                continue
            if check_cache(link, archive_tasks):
                print(f"    Skipping {task_name} as it is already in archive")
                continue
            print(f"    Creating task {task_name} in inbox")
            # dida_client.create_inbox_task(access_token, task_name)
            # time.sleep(3)


if __name__ == "__main__":
    main()
