from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
import os
from fish_util.src.log_util import FishLogger
import subprocess
from fish_script.client import devonthink_client, eagle_client
from pydantic import BaseModel
import wucai_client
from fastapi import FastAPI, HTTPException
from celery.result import AsyncResult
from celery_client import celery_app, url2md
import email_client
import devonthink_client

logger = FishLogger(__file__)
print = logger.debug

app = FastAPI()

# 添加CORS中间件，允许对所有来源的访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源访问
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EagleRequest(BaseModel):
    image_url: str
    zj_url: str
    folder_id: str
    file_name: str


class DevonthinkWeblocRequest(BaseModel):
    title: str
    url: str


class DevonthinkMarkdownRequest(BaseModel):
    url: str


class SaveDevonthinkMarkdownRequest(BaseModel):
    url: str
    title: str
    content: str


@app.get("/")
async def get_request_info(request: Request):
    client_host = request.client.host
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"current_time": current_time, "client_ip": client_host}


@app.post("/add/devonthink/webloc")
async def add_devon_think(request: DevonthinkWeblocRequest):
    title = request.title
    url = request.url
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Received title: {title}, url: {url} at {current_time}")
    devonthink_client.create_webloc_record(title, url)
    return {
        "title": title,
        "url": url,
        "current_time": current_time,
    }


@app.post("/add/devonthink/markdown")
async def add_devon_think_markdown(request: DevonthinkMarkdownRequest):
    url = request.url
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Received url: {url} at {current_time}")
    # devonthink_client.create_webloc_record(title, url)
    task = url2md.delay(url)
    print(f"Task id: {task.id}")
    return {
        "url": url,
        "current_time": current_time,
        "task_id": task.id,
    }


@app.post("/save/devonthink/markdown")
async def save_devon_think_markdown(request: SaveDevonthinkMarkdownRequest):
    url = request.url
    title = request.title
    content = request.content
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Received url: {url} at {current_time}")
    devonthink_client.create_markdown_record(url, title, content)
    return {
        "url": url,
        "title": title,
        "content": len(content),
        "current_time": current_time,
    }


@app.post("/add/eagle")
async def add_eagle(request: EagleRequest):
    # data = await request.json()
    # image_url = data["image_url"]
    # zj_url = data["zj_url"]
    # folder_id = data["folder_id"]
    image_url = request.image_url
    zj_url = request.zj_url
    folder_id = request.folder_id
    file_name = request.file_name
    # client_host = request.client.host
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"Received image_url: {image_url}, zj_url: {zj_url}, zj_folder_id: {folder_id}  at {current_time}"
    )
    eagle_client.add_item(image_url, zj_url, folder_id, file_name)
    return {
        "image_url": image_url,
        "zj_url": zj_url,
        "folder_id": folder_id,
        "current_time": current_time,
        # "client_ip": client_host,
    }


@app.get("/wucai/sync")
async def wucai_sync(request: Request):
    # data = await request.json()
    # image_url = data["image_url"]
    # zj_url = data["zj_url"]
    # folder_id = data["folder_id"]
    client_host = request.client.host
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    wucai_client.main()
    return {
        "current_time": current_time,
        "client_ip": client_host,
        "methond": "wucai_sync",
    }


@app.get("/hugo/publish")
async def hugo_publish(request: Request):
    client_host = request.client.host
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    process = subprocess.Popen(
        "/bin/bash /Users/yutianran/Documents/MyCode/MyScript/blog-hugo/build_server.sh",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # 获取命令执行结果
    output, error = process.communicate()
    # 打印命令执行结果
    print(
        f"Output: {output.decode()}",
    )
    print(f"Error: {error.decode()}")
    return {
        "current_time": current_time,
        "client_ip": client_host,
        "methond": "hugo_publish",
    }


@app.get("/dida/redirect_uri")
async def redirect_uri_get(state: str, code: str):
    print(f"Received state: {state}, code: {code}")
    return {"state": state, "code": code}


@app.post("/tasks/")
def create_task(url: str):
    task = url2md.delay(url)
    return {"task_id": task.id}


@app.get("/tasks/{task_id}")
def get_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    result = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }
    return result


# celery -A celery_client inspect active
# celery -A celery_client inspect scheduled
@app.get("/task/active")
def get_active_tasks():
    i = celery_app.control.inspect()
    active_tasks = i.active()  # 获取所有worker的活动任务
    sizes = get_active_tasks_size(active_tasks)
    return {"sizes": sizes, "active_tasks": active_tasks}


# 获取active_tasks中每个任务列表的大小
def get_active_tasks_size(active_tasks):
    sizes = {}
    for task_name, task_list in active_tasks.items():
        sizes[task_name] = len(task_list)
    return sizes


# Celery任务成功后的回调
# @url2md.after_return.connect
# def task_done(sender, result, **kwargs):
# email_client.send_email("Your task is completed. Result file")


print("Starting FastAPI server at http://localhost:18001/docs")

if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=18001, reload=True)
    # os.system("uvicorn fastapi_client:app --host 0.0.0.0 --port 18001 --reload")
    # 使用 subprocess.Popen 执行命令
    process = subprocess.Popen(
        "cd /Users/yutianran/Documents/MyCode/MyScript/fish_script/client && uvicorn fastapi_client:app --host 0.0.0.0 --port 18001 --reload >> fastapi_client.log 2>&1 &",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # 获取命令执行结果
    output, error = process.communicate()
    # 打印命令执行结果
    print(
        f"Output: {output.decode()}",
    )
    print(f"Error: {error.decode()}")
    # os.system("nohup uvicorn fastapi_client:app --host 0.0.0.0 --port 38002 &")
