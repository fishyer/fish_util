import os
import re
import time
import urllib3
import frontmatter
import uuid
from wfapi import *
import fish_util.src.client.dida_client as dida_client
from fish_util.src.client.dida_client import DidaTask
import fish_util.src.decorator_util as decorator_util
from fish_util.src.client.ezlogger import print, debug, error, warning, info
import fish_util.src.client.env_client as env_client
import fish_util.src.client.jina_client as jina_client
import fish_util.src.client.jianguoyun_client as jianguoyun_client


# 禁止显示urllib3库发出的关于不安全请求的警告信息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 记录已经完成的WF节点名
completed_node_set = set()


def get_nodes(inbox: Node, nodes, node_set, recursion=True):
    for i in inbox:
        if i.name not in node_set:
            print(f"Normal Node: {i.name}, {i.description}, {i.is_completed}")
            node_set.add(i.name)
            if not i.is_completed:
                nodes.append(i)
            # 处理子节点
            if recursion:
                if i.name.startswith("BookMark-") or i.name.startswith("MarkSearch-"):
                    get_nodes(i, nodes, node_set, recursion)
        else:
            print(f"Duplicate node: {i.name} {i.description} {i.is_completed}")
            i.delete()
    # print(nodes)
    # print(node_set)
    return nodes


# 添加WF节点
def add(node: Node, title: str, content: str = None):
    for i in node:
        if i.name == title:
            print(f"Node {title} already exists, skip.")
            return i
    sub_node = node.create()
    sub_node.edit(title)
    if content:
        sub_node.description = content
    return sub_node


@decorator_util.trace_exception
@decorator_util.trace_retry(3, 5)
def process_dida_task(inbox, task: DidaTask):
    dida_title, dida_url = preprocess(task.title, task.content)
    if dida_url:
        # 添加wf节点
        node = add(inbox, dida_title, dida_url)
        # 删除滴答清单任务
        dida_client.delete_task(
            env_client.dida_access_token, env_client.dida_inbox_id, task.id
        )
        return node
    else:
        # print(f"No url found in {task.title}")
        return None


# 借助坚果云生成一篇obsidian笔记，大概需要5秒-10秒左右
@decorator_util.trace_exception
@decorator_util.trace_retry(3, 5)
def process_workflowy_node(node: Node):
    global completed_node_set
    if node.is_completed:
        print(f"Skipping completed node: {node.name}")
        return
    # 之所以需要completed_node_set缓存，是因为WorkFlowy刷新时，完成状态更新太慢，会导致重复处理
    if node.name in completed_node_set:
        print(f"Skipping cached completed node: {node.name}")
        node.complete()
        return
    dida_title, dida_url = preprocess(node.name, node.description)
    # print(f"Processing node: {node.name} {dida_title} {dida_url}")
    if dida_url:
        info(f"Generating obsidian note for {dida_title} with url {dida_url}...")
        # 获取Jina的markdown内容
        jina_title, jina_url, content = jina_client.get_markdown_by_url(dida_url)
        # 添加ob笔记
        post = frontmatter.loads(content)
        id = str(uuid.uuid4())
        post["id"] = id
        post["title"] = dida_title
        post["url_source"] = dida_url
        obsidian_link = f"obsidian://advanced-uri?vault={env_client.ob_vault}&uid={id}"
        post["obsidianLink"] = obsidian_link
        fm_content = frontmatter.dumps(post)
        # 写入本地文件
        simple_title = jina_client.sanitize_title_for_filename(dida_title)
        local_path = f"cache/md/{env_client.webdav_username}/{simple_title}.md"
        local_folder = os.path.dirname(local_path)
        # 先检查本地缓存目录是否存在，不存在则创建
        if not os.path.exists(local_folder):
            os.makedirs(local_folder, exist_ok=True)
        # 再检查本地缓存文件是否存在，存在则跳过
        if os.path.exists(local_path):
            info(f"Local cache file {local_path} exists, skip.")
            return
        remote_path = f"/{jianguoyun_client.remote_folder}/{simple_title}.md"
        with open(local_path, "w") as f:
            f.write(fm_content)
        if jianguoyun_client.upload_file(local_path, remote_path):
            # 借助obsidian插件Local REST API来新建笔记文件
            # generate_obsidian_note(simple_title, fm_content)
            add(node, obsidian_link)
            node.complete()
            completed_node_set.add(node.name)
    else:
        info(f"No url to generate obsidian note in {node.name} {dida_title} {dida_url}")


# 预处理，从WF节点的标题和备注中提取出title和url
# @decorator_util.trace_args
def preprocess(name, description):
    if name is not None:
        name_title, name_url = re_match_url(name)
        if name_url:
            return get_value(name_title, name), name_url
    if description is not None:
        description_title, description_url = re_match_url(description)
        if description_url:
            return get_value(description_title, name), description_url
    return None, None


def get_value(expect_value, default_value):
    if not is_empty_string(expect_value):
        return expect_value
    return default_value


def is_empty_string(s):
    return s is None or s.strip() == ""


def re_match_url(text):
    # https://mp.weixin.qq.com/s/avtP7m8SKX9BKYNgDajBsg
    if text.startswith("http"):
        return None, text
    # <a href="https://mp.weixin.qq.com/s/avtP7m8SKX9BKYNgDajBsg"></a>
    if match := re.match(r'<a\s*href="([^"]*)"\s*>', text):
        return None, match.group(1)
    # [文章标题](<a href="https://juejin.cn">https://juejin.cn/post/7373831659470880806</a>)
    if match := re.match(r"\[(.*?)\]\(<a\s+href=\".*?\">(.*?)</a>\)", text):
        return match.group(1), match.group(2)
    # [文章标题](https://juejin.cn/post/7373831659470880806)
    if match := re.match(r"\[(.*?)\]\((.*?)\)", text):
        return match.group(1), match.group(2)
    return None, None


# @decorator_util.trace_exception
@decorator_util.trace_retry(3, 5)
def get_wf():
    wf = Workflowy(sessionid=env_client.wf_session_id)
    return wf


def get_inbox(wf: Workflowy, inbox_name: str):
    root = wf.root
    for child in root:
        if child.name == inbox_name:
            info(f"Inbox exists: {inbox_name}")
            return child
    inbox = root.create()
    inbox.edit(inbox_name)
    info(f"Inbox created: {inbox_name}")
    return inbox


def get_dida_inbox(wf: Workflowy):
    return get_inbox(wf, env_client.wf_inbox_name)


def dida2wf():
    inbox_tasks = dida_client.get_project_by_id(
        env_client.dida_access_token, env_client.dida_inbox_id
    )
    info(f"Inbox Tasks: {len(inbox_tasks)}")
    for i, task in enumerate(inbox_tasks):
        # print(f"{i+1}. {task.title}")
        node = process_dida_task(inbox, task)
        if node is not None:
            process_workflowy_node(node)
        # 等待1秒，防止滴答清单接口频繁请求而报错500
        # time.sleep(1)
    info("Export Dida[inbox] to Workflowy Done.")


def wf2ob():
    global completed_node_set
    info("Start to export Workflowy[inbox] to Obsidian...")
    for node in normal_nodes:
        process_workflowy_node(node)
    info("Export Workflowy[inbox] to Obsidian Done.")


def init_wf():
    global wf
    info("Start to connect to Workflowy...")
    wf = get_wf()
    info("Connected to Workflowy.")


def refresh_inbox():
    global inbox, nodes, node_set, normal_nodes
    info("Refreshing inbox...")
    inbox = get_dida_inbox(wf)
    info(f"Inbox: {inbox.name} len(inbox): {len(inbox)}")
    nodes = []
    node_set = set()
    normal_nodes = get_nodes(inbox, nodes, node_set, recursion=True)
    info(
        f"Got Normal Node Count: {len(normal_nodes)}  completed={len(completed_node_set)}"
    )


def import_from_dict(dict_list, inbox_name, check_duplicate=True):
    """
    从dict_list导入数据
    [
        {
            "title": "领导让前端实习生在网页上添加一个长时间不操作锁定电脑的功能",
            "content": "https://juejin.cn/post/7373831659470880806"
        }
    ]
    """
    inbox_node = get_inbox(wf, inbox_name)
    node_list = []
    for item in dict_list:
        title = item["title"]
        content = item["content"]
        if title and content:
            if check_duplicate and title in node_set:
                print(f"Duplicate node at import: {title} {content}")
                continue
            node = add(inbox_node, title, content)
            node_list.append(node)
    # 因为处理节点比较耗时，所以等批量导入节点完成以后再来批量处理节点
    for node in node_list:
        process_workflowy_node(node)


def main():
    print(__file__)
    init_wf()
    refresh_inbox()
    # dida2wf()
    # wf2ob()
    # title, url = preprocess(
    #     "领导让前端实习生在网页上添加一个长时间不操作锁定电脑的功能",
    #     r'<a href="https://juejin.cn/post/7373831659470880806">https://juejin.cn/post/7373831659470880806</a>',
    # )

    # print(f"title: {title}, url: {url}")


if __name__ == "__main__":
    main()
