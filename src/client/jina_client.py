import requests
import re
import arrow
from fish_util.src.log_util import print
import yaml
import fish_util.src.client.bookmark_client
import fish_util.src.client.markdown_client as md_client
import random
import fish_util.src.time_util as time_util
import fish_util.src.file_util as file_util
import aiohttp
import asyncio
import uuid
from fish_util.src.log_util import FishLogger

logger = FishLogger(__file__)
print = logger.debug


# 添加frontmatter到Markdown内容中
def add_frontmatter(title, url_source, markdown_content):
    note_uuid = uuid.uuid4()
    # print(f"note_uuid: {note_uuid}")
    frontmatter = {"title": title, "url_source": url_source, "id": str(note_uuid)}
    frontmatter_text = yaml.dump(frontmatter, allow_unicode=True)
    content_with_frontmatter = f"---\n{frontmatter_text}---\n\n{markdown_content}"
    return content_with_frontmatter


# 使用正则表达式分别匹配三个关键信息：Title, URL Source, Markdown Content
def extract_info_from_content(content):
    title_pattern = r"Title: (.*?)\n"
    url_pattern = r"URL Source: (.*?)\n"
    markdown_pattern = r"Markdown Content:\n(.*)"

    title_match = re.search(title_pattern, content)
    url_match = re.search(url_pattern, content)
    markdown_match = re.search(markdown_pattern, content, re.DOTALL)

    if title_match and url_match and markdown_match:
        title = title_match.group(1).strip()
        url_source = url_match.group(1).strip()
        markdown_content = markdown_match.group(1).strip()
        return title, url_source, markdown_content
    else:
        raise ValueError("Failed to extract info from content")


# 去除标题中的非法字符，并将空格替换为空, 用于生成文件名
def sanitize_title_for_filename(title):
    illegal_chars = r'[\\/*?:"<>|]'
    sanitized_title = re.sub(illegal_chars, "_", title)  # 非法字符替换为下划线
    sanitized_title = sanitized_title.replace(" ", "")  # 空格替换为空
    return sanitized_title


def get_markdown_by_url(src_url):
    jina_url = f"https://r.jina.ai/{src_url}"
    webpage_content = request_content(jina_url)
    title, url_source, markdown_content = extract_info_from_content(webpage_content)
    return title, url_source, markdown_content


def get_markdown_from_url(src_url):
    jina_url = f"https://r.jina.ai/{src_url}"
    webpage_content = request_content(jina_url)
    return parse_content(webpage_content)


async def async_get_markdown_from_url(src_url):
    jina_url = f"https://r.jina.ai/{src_url}"
    content = await async_request_content(jina_url)
    return parse_content(content)


def request_content(url):
    response = requests.get(url)
    return response.text


async def async_request_content(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()
            return content


def parse_content(webpage_content):
    random_name = str(random.randint(1000, 9999))
    current_time = arrow.now().format("YYYYMMDD_HHmmss")
    temp_file_name = f"cache/markdown/urls/{current_time}_{random_name}.md"
    file_util.write_file(temp_file_name, webpage_content)
    title, url_source, markdown_content = extract_info_from_content(webpage_content)
    markdown_with_frontmatter = add_frontmatter(title, url_source, markdown_content)
    return title, markdown_with_frontmatter


def get_test_links():
    urls = [
        "https://segmentfault.com/a/1190000044752197",
        "https://juejin.cn/post/7303847314896175116",
        "https://mp.weixin.qq.com/s/c9bLvq9VFx80_XmEuis2_g",
        "https://zhuanlan.zhihu.com/p/615927252",
    ]
    links = []
    for url in urls:
        links.append({"title": "", "url": url})
    return links


def get_links_from_bookmark():
    note_dir = time_util.get_time_dir("note/clipper")
    bar_folder, other_folder = bookmark_client.get_bookmarks()
    parsed_links = bookmark_client.get_links_from_folder(other_folder)
    spider_links(parsed_links, note_dir)


def get_links_from_mdfile():
    note_dir = time_util.get_time_dir("test")
    file_path = "/Users/yutianran/Documents/MyNote/daily/2024/05/2024-05-18.md"
    parsed_links = md_client.parse_links_from_mdfile(file_path)
    md_client.create_file_from_links(parsed_links, f"{note_dir}/links_all.md")
    # spider_links(parsed_links, note_dir)
    return parsed_links


async def async_get_links_from_mdfile():
    print("async_get_links_from_mdfile")
    note_dir = time_util.get_time_dir("note/clipper")
    file_path = "/Users/yutianran/Documents/MyPKM/note/002-Project/daily/2024-05-08.md"
    parsed_links = md_client.parse_links_from_mdfile(file_path)
    md_client.create_file_from_links(parsed_links, f"{note_dir}/links_all.md")
    await batch_async_spider_links(parsed_links, note_dir)


def spider_links(parsed_links, note_dir):
    success_links = []
    failed_links = []
    for i, item in enumerate(parsed_links):
        name = item["title"]
        url = item["url"]
        print(f"    {i+1}. {name} {url}")
        try:
            title, md_content = get_markdown_from_url(url)
            md_path = f"{note_dir}/{sanitize_title_for_filename(title)}.md"
            file_util.write_file(md_path, md_content)
        except Exception as e:
            print(f"    Failed to spider {item}, error: {e}")
            failed_links.append(item)
    md_client.create_file_from_links(failed_links, f"{note_dir}/links_failed.md")
    md_client.create_file_from_links(success_links, f"{note_dir}/links_success.md")


# 异步爬取，主要流程参考spider_links，但是使用 async_get_markdown_from_url 代替 get_markdown_from_url
async def async_spider_links(parsed_links, note_dir):
    success_links = []
    failed_links = []

    tasks = []
    for i, item in enumerate(parsed_links):
        name = item["title"]
        url = item["url"]
        print(f"    {i+1}. {name} {url}")
        try:
            task = asyncio.create_task(async_get_markdown_from_url(url))
            tasks.append((item, task))  # 保存对应的链接和异步任务
        except Exception as e:
            print(f"    Failed to start task for {item}, error: {e}")
            failed_links.append(item)

    # 等待所有异步任务完成
    for item, task in tasks:
        try:
            title, md_content = await task
            md_path = f"{note_dir}/{sanitize_title_for_filename(title)}.md"
            file_util.write_file(md_path, md_content)
            success_links.append(item)
        except Exception as e:
            print(f"    Failed to spider {item}, error: {e}")
            failed_links.append(item)

    md_client.create_file_from_links(failed_links, f"{note_dir}/links_failed.md")
    md_client.create_file_from_links(success_links, f"{note_dir}/links_success.md")


async def batch_async_spider_links(parsed_links, note_dir):
    success_links = []
    failed_links = []

    # sem = asyncio.Semaphore(10)

    async def fetch_url(idx, item, note_dir):  # 添加idx参数用于传递任务下标
        name = item["title"]
        url = item["url"]
        print(f"    {idx+1}. {name} {url}")
        # async with sem:
        try:
            # asyncio.sleep(random.randint(1, 3))  # 模拟网络请求延迟
            title, md_content = await async_get_markdown_from_url(url)
            md_path = f"{note_dir}/{sanitize_title_for_filename(title)}.md"
            file_util.write_file(md_path, md_content)
            success_links.append(item)
            print(f"    Successfully processed task {idx+1}: {item}")
        except Exception as e:
            failed_links.append(item)
            print(f"    Failed to process task {idx+1}: {item}, error: {e}")

    # 分批处理任务
    # tasks = [fetch_url(sem, i, item, note_dir) for i, item in enumerate(parsed_links)]  # 传递任务下标
    # await asyncio.gather(*tasks)
    # 分批处理任务
    batch_size = 20
    chunked_lists = [
        parsed_links[i : i + batch_size]
        for i in range(0, len(parsed_links), batch_size)
    ]
    for i, chunk in enumerate(chunked_lists):
        print(f"Processing chunk {i+1}/{len(chunked_lists)}")
        batch_tasks = [
            fetch_url(i * batch_size + j, item, note_dir)
            for j, item in enumerate(chunk)
        ]
        await asyncio.gather(*batch_tasks)

    md_client.create_file_from_links(failed_links, f"{note_dir}/links_failed.md")
    md_client.create_file_from_links(success_links, f"{note_dir}/links_success.md")


def main():
    print(__file__)
    # asyncio.run(async_get_links_from_mdfile())
    # urls = get_links_from_mdfile()  # 你的urls列表
    # # 将urls列表拆分成多个20个一组的小列表
    # batch_size = 20
    # chunked_lists = [urls[i:i+batch_size] for i in range(0, len(urls), batch_size)]
    # print(f"Total {len(urls)} links, split into {len(chunked_lists)} chunks")
    # for i, chunk in enumerate(chunked_lists):
    #     print(f"Processing chunk {i+1}/{len(chunked_lists)}")
    get_links_from_mdfile()


if __name__ == "__main__":
    main()
    # note_uuid = uuid.uuid4()
    # print(note_uuid)
