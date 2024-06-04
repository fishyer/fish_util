from wfapi import *
import dida_client
from dida_client import DidaTask
import devonthink_client
import jina_client
import markdown_client
import arrow
import requests
import uuid
import frontmatter
import re
from dataclasses import dataclass
from urllib.parse import quote

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


import fish_util.src.decorator_util as decorator_util

from fish_util.src.log_util import FishLogger

logger = FishLogger(__file__)
print = logger.debug


def add(node: Node, title: str, content: str = None):
    sub_node = node.create()
    sub_node.edit(title)
    if content:
        sub_node.description = content
    return sub_node


# 用正则判断是否是[]()的格式
def is_mdlink(text: str):

    pattern = r"\[(.*?)\]\((.*?)\)"
    match = re.match(pattern, text)
    if match:
        return match.group(1), match.group(2)
    else:
        return None


# 用正则判断是否是title url的格式
def is_url_in_title(text: str):
    pattern = r"^(.*)\s(http.*?)$"
    match = re.match(pattern, text)
    if match:
        return match.group(1), match.group(2)
    else:
        return None


@dataclass
class Record:
    title: str
    content: str
    url: str
    title2: str
    dt_link: str


def add_devonthink(url, title):
    title2, content = jina_client.get_markdown_from_url(url)
    record = devonthink_client.create_markdown_record_in_db(url, title, content)
    dt_link = f"x-devonthink-item://{record.uuid}"
    generate_obsidian_note(title, content)
    return Record(title, content, url, title2, dt_link)


def generate_obsidian_note(title, content):
    simple_title = jina_client.sanitize_title_for_filename(title)
    url = f"https://66.112.214.250:27124/vault/dida/{simple_title}.md"
    payload = content.encode("utf-8")
    headers = {
        "Authorization": "Bearer a38314cb76a2a4f3c5a31f1c4c65e3ac622c736b6dd5456d7d24578dbeab6c49",
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Content-Type": "text/markdown",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }
    # print(url)
    response = requests.request("PUT", url, headers=headers, data=payload, verify=False)
    if response.status_code != 204:
        print(response.status_code)


ob_vault = "MyNote"
access_token = "3ad46d12-a0d6-454d-8ccc-e3bbce0aa943"
inbox_project_id = "inbox1010592152"
archive_project_id = "664cc4c1a20203c5258687e7"


@decorator_util.trace_exception
@decorator_util.trace_retry(3, 5)
def process_dida_task(inbox, task: DidaTask):
    dida_title, dida_url = preprocess(task.title, task.content)
    if dida_url:
        # print(f"Processing {dida_title} with url {dida_url}...")
        jina_title, jina_url, content = jina_client.get_markdown_by_url(dida_url)
        post = frontmatter.loads(content)
        id = str(uuid.uuid4())
        # 添加wf节点
        node = add(inbox, dida_title, dida_url)
        # 添加ob笔记
        post["id"] = id
        post["title"] = dida_title
        post["url_source"] = dida_url
        obsidian_link = f"obsidian://advanced-uri?vault={ob_vault}&uid={id}"
        post["obsidianLink"] = obsidian_link
        # 更新滴答清单的信息
        task.title = f"[{dida_title}]({dida_url})"
        task.tags.append("obsidian")
        update_time = arrow.now().format("YYYY-MM-DD HH:mm:ss")
        task.content = f"update_time: {update_time}\nobsidianLink: {obsidian_link}\n[link]({obsidian_link})"
        task.projectId = archive_project_id
        dida_client.delete_task(access_token, inbox_project_id, task.id)
        new_task = dida_client.create_task(access_token, task)
        dida_link = (
            f"https://dida365.com/webapp#p/{archive_project_id}/tasks/{new_task.id}"
        )
        post["didaLink"] = dida_link
        # print(dida_link)
        add(node, dida_link)
        add(node, obsidian_link)
        fm_content = frontmatter.dumps(post)
        generate_obsidian_note(dida_title, fm_content)
    else:
        print(f"No url found in {task.title}")


# 预处理，从滴答清单的标题和内容中提取出title和url
def preprocess(title, content):
    if match := re.match(r"\[(.*?)\]\((.*?)\)", title):
        return match.group(1), match.group(2)
    if content is not None and content.startswith("http"):
        return title, content
    if title is not None and title.startswith("http"):
        return title, title
    return None, None


@decorator_util.trace_exception
@decorator_util.trace_retry(3, 5)
def get_wf():
    wf = Workflowy(username="yutianran666@gmail.com", password="workflowy132850")
    # wf = Workflowy(sessionid="bza32axq7bbzt9w5h1k6b163v017jviz")
    return wf


def get_dida_inbox(wf: Workflowy):
    root = wf.root
    inbox_name = "滴答清单-Inbox"
    for child in root:
        if child.name == inbox_name:
            print(f"Inbox exists: {child.name}")
            return child
    inbox = root.create()
    inbox.edit(inbox_name)
    print(f"Inbox created: {inbox.name}")
    return inbox


def dida2wf():
    print("Start to connect to Workflowy...")
    wf = get_wf()
    print("Connected to Workflowy.")

    inbox = get_dida_inbox(wf)
    print(f"Inbox: {inbox.name}")

    inbox_tasks = dida_client.get_project_by_id(access_token, inbox_project_id)
    print(f"Inbox Tasks: {len(inbox_tasks)}")
    for i, task in enumerate(inbox_tasks):
        print(f"{i+1}. {task.title}")
        process_dida_task(inbox, task)

    print("Export Dida[inbox] to Workflowy Done.")


def main():
    print(__file__)
    # title, url = is_title_url(
    #     "2024年我的生产力工具集 - Tony Xu Blog https://tonyxu.io/blog/2024-productivity-tools/"
    # )
    # print(f"title:{title},url:{url}")
    dida2wf()
    # url = "https://juejin.cn/post/7327480122407141388"
    # title = "在上海做程序员这么多年，退休后我的工资是多少？ - 掘金"
    # dt_link = add_devonthink(url, title)
    # print(dt_link)


if __name__ == "__main__":
    main()
    # t, u = preprocess(
    #     "[Lantz，一个非常有用的Python库](http://mp.weixin.qq.com/s?__biz=MzkzOTY3NDg1Nw==&mid=2247483769&idx=2&sn=a52949679b7d67be58e45bf7382e17b0&chksm=c2ec1cfff59b95e9bf4bf65d26a387325d38e9b14e4bb67371f0ff0a438f5fe2a3f7cebc7b1a&mpshare=1&scene=1&srcid=0522dDS46vZ9hY7hrAqvVIa9&sharer_shareinfo=774707b9fcfdb520ce97393490ce4a1d&sharer_shareinfo_first=774707b9fcfdb520ce97393490ce4a1d#rd)",
    #     "",
    # )
    # print(t)
    # print(u)
    # request_obsidian_note("test", "test")
