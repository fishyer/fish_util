# celery_utils.py

from celery import Celery
import time
import jina_client
import asyncio
from pydt3 import DEVONthink3
import requests
import json

# celery -A celery_client worker --loglevel=warning
# 创建 Celery 应用实例
celery_app = Celery(
    "celery_client",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)


# 定义任务函数
@celery_app.task
def add(x, y):
    print(f"x: {x}, y: {y}")
    return x + y


@celery_app.task
def url2md(url):
    print(f"url: {url}")
    title, md_content = asyncio.run(jina_client.async_get_markdown_from_url(url))
    print(f"title: {title} url: {url}")
    print(f"md_content: len={len(md_content)}")
    return url, title, md_content


from celery.signals import task_success


@task_success.connect
def task_done(sender=None, result=None, **kwargs):
    if sender.name == "celery_client.add":
        # 处理 add 任务完成的逻辑
        print(f"Add 任务完成，结果为: {result}")
    elif sender.name == "celery_client.url2md":
        # 处理 url2md 任务完成的逻辑
        url, title, md_content = result
        print(f"url2md 任务完成，标题为: {title}, 内容长度为: {len(md_content)}")

        # 发送post请求
        api_url = "http://localhost:18001/save/devonthink/markdown"
        payload = json.dumps({"url": url, "title": title, "content": md_content})
        headers = {
            "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Host": "localhost:18001",
            "Connection": "keep-alive",
        }
        response = requests.request("POST", api_url, headers=headers, data=payload)
        print(f"Devonthink 保存结果: {response.text}")
    else:
        # 处理其他任务完成的逻辑
        print(f"未知任务 {sender.name} 完成，结果为: {result}")
