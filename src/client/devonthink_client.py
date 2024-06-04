from pydt3 import DEVONthink3
import fish_util.src.file_util as file_util
import asyncio
import jina_client
import celery_client

dt = DEVONthink3()


def create_webloc_record(name, url):
    # 获取Inbox数据库
    inbox_db = dt.inbox
    # 获取readlater子组
    # readlater_group = dt.create_location("bookmark", inbox_db)
    readlater_group = dt.create_location("bookmark", inbox_db)
    # 添加webloc书签到readlater子组
    bookmark = dt.create_record_with(
        {
            "name": name,
            "type": "bookmark",
            "URL": url,
        },
        readlater_group,
    )
    print(bookmark)
    return bookmark


def url2md(url):
    url = "https://mp.weixin.qq.com/s/IXcxlzvW-SURGOHEdUDrbg"
    result = celery_client.url2md.delay(url)
    print(f"task: {result}")
    title, md_content = result.get()
    print(f"title: {title}")


def create_markdown_record(url, title, content):
    # print(f"url: {url}")
    # print(f"title: {title}")
    # print(f"content: len={len(content)}")
    devonthink = DEVONthink3()
    # 存到devonthink
    inbox_db = devonthink.inbox
    test_group = dt.create_location("test", inbox_db)
    md = dt.create_record_with(
        {
            "name": jina_client.sanitize_title_for_filename(title),
            "type": "markdown",
            "URL": url,
            "content": content,
        },
        test_group,
    )
    # print(md)
    return md


def get_database_by_name(name):
    devonthink = DEVONthink3()
    for db in devonthink.databases:
        if db.name == name:
            return db


def create_markdown_record_in_db(url, title, content):
    # print(f"url: {url}")
    # print(f"title: {title}")
    # print(f"content: len={len(content)}")
    # for db in devonthink.databases:
    #     print(db.name)
    #     if db.name == "MyDevon":
    #         test_group = dt.create_location("pap.er", db)
    #         name = test_group.name
    #         print(name)
    # 存到devonthink
    inbox_db = get_database_by_name("MyDevon")
    test_group = dt.create_location("pap.er", inbox_db)
    md = dt.create_record_with(
        {
            "name": jina_client.sanitize_title_for_filename(title),
            "type": "markdown",
            "URL": url,
            "content": content,
        },
        test_group,
    )
    return md


def main():
    # [在上海做程序员这么多年，退休后我的工资是多少？-掘金](x-devonthink-item://0A076CF2-4EE7-4AC7-A065-ECA93F9C8E5D)
    print(__file__)
    url = "https://juejin.cn/post/7327480122407141388"
    title = "在上海做程序员这么多年，退休后我的工资是多少？ - 掘金"
    md_content = "len=9064"
    node = create_markdown_record_in_db(url, title, md_content)
    # node_uuid = node.uuid
    # node_url = f"x-devonthink-item://{node_uuid}"
    # # x-devonthink-item://70211FBA-4ED1-49E8-8F48-1512EFD13457
    # print(f"[{title}]({node_url} )")
    # print(node)


if __name__ == "__main__":
    main()
