import subprocess
import requests
import json
from urllib import parse
import pydantic
from typing import Optional
import arrow
from fish_util.src.log_util import FishLogger

logger = FishLogger(__file__)
print = logger.debug


class DidaTask(pydantic.BaseModel):
    """
        {
        "id": "664aa60be4b01213542d1f62",
        "projectId": "inbox1010592152",
        "sortOrder": -2033688601493525,
        "title": "RW-title-2 #MarkSearch",
        "timeZone": "Asia/Shanghai",
        "isAllDay": false,
        "priority": 0,
        "status": 0,
        "startDate": "2024-05-20T02:00:00.000+0000",
        "dueDate": "2024-05-20T04:40:00.000+0000",
    }
    """

    id: Optional[str]
    projectId: str
    title: str
    sortOrder: Optional[int]
    content: Optional[str] = None
    desc: Optional[str] = None
    timeZone: Optional[str]
    isAllDay: Optional[bool]
    priority: Optional[int]
    status: Optional[int]
    tags: Optional[list] = []
    columnId: Optional[str] = None
    startDate: Optional[str] = None
    dueDate: Optional[str] = None
    reminders: Optional[list] = []
    repeatFlag: Optional[str] = None


class DidaProject(pydantic.BaseModel):
    """
    {
        "id": "6529e53ba7105b45e836a273",
        "name": "MarkSearch",
        "color": "#007bff",
        "sortOrder": 4611686018426048511,
        "groupId": "6529e5a4a7105b45e836a2cd",
        "viewMode": "list",
        "permission": "write",
        "kind": "TASK"
    }
    """

    id: str
    name: str
    color: Optional[str]
    sortOrder: int
    groupId: Optional[str]
    viewMode: Optional[str]
    permission: Optional[str]
    kind: str


def execute_command(command):
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output, error = process.communicate()
    result = output.decode()
    error = error.decode()
    if error:
        print(error)
    return result


# https://dida365.com/oauth/authorize?scope=tasks:write%20tasks:read&client_id=13TIYIw0ik1FxqLREs&state=Ups0YwpHwWF1yoct&redirect_uri=https://fastapi.fishyer.com/dida/redirect_uri&response_type=code
def authorize():
    """
    {
      "state": "Ups0YwpHwWF1yoct",
      "code": "MJQFC0"
    }
    """
    # url = "
    scope = "tasks:write%20tasks:read"
    client_id = "13TIYIw0ik1FxqLREs"
    state = "Ups0YwpHwWF1yoct"
    redirect_uri = "https://fastapi.fishyer.com/dida/redirect_uri"
    response_type = "code"
    url = f"https://dida365.com/oauth/authorize?scope={scope}&client_id={client_id}&state={state}&redirect_uri={redirect_uri}&response_type={response_type}"
    print(url)


# 3ad46d12-a0d6-454d-8ccc-e3bbce0aa943
def get_access_token(code):
    """
        {
        "access_token": "3ad46d12-a0d6-454d-8ccc-e3bbce0aa943",
        "token_type": "bearer",
        "expires_in": 15417371,
        "scope": "tasks:read tasks:write"
    }
    """
    url = "https://dida365.com/oauth/token"
    client_id = "13TIYIw0ik1FxqLREs"
    client_secret = "%yZ2_4a$S9DdA46F5+l)jtIVe9spOM0^"
    grant_type = "authorization_code"
    scope = "tasks:write tasks:read"
    redirect_uri = "https://fastapi.fishyer.com/dida/redirect_uri"
    formData = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": grant_type,
        "scope": scope,
        "redirect_uri": redirect_uri,
    }
    data = parse.urlencode(formData)
    headers = {
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Host": "dida365.com",
        "Connection": "keep-alive",
    }
    response = requests.request("POST", url, headers=headers, data=data)
    print(response.text)
    json_data = json.loads(response.text)
    if json_data.get("error"):
        print(json_data.get("error"))
        print(json_data.get("error_description"))
        return
    access_token = json_data["access_token"]
    token_type = json_data["token_type"]
    expires_in = json_data["expires_in"]
    scope = json_data["scope"]
    print(f"access_token: {access_token}")
    print(f"token_type: {token_type}")
    print(f"expires_in: {expires_in}")
    print(f"scope: {scope}")


def get_projects(access_token):
    url = "https://dida365.com/open/v1/project"
    print(url)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Accept": "*/*",
        "Host": "dida365.com",
        "Connection": "keep-alive",
    }
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
    json_data = json.loads(response.text)
    if "error" in json_data:
        print(json_data.get("error"))
        print(json_data.get("error_description"))
        return
    projects = [DidaProject.parse_obj(item) for item in json_data]
    for i, project in enumerate(projects):
        print(i, project.id, project.name)
    return projects


# 664aa740e4b0864437b7a137
def create_inbox_task(access_token, task_name):
    task = DidaTask(
        projectId="inbox1010592152",
        title=task_name,
    )
    return create_task(access_token, task)


def create_task(access_token, task: DidaTask):
    url = "https://dida365.com/open/v1/task"
    payload = json.dumps(task.dict(exclude_none=True))
    headers = {
        "Authorization": "Bearer " + access_token,
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Host": "dida365.com",
        "Connection": "keep-alive",
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        print(response.status_code)
        return None
    json_data = json.loads(response.text)
    if "error" in json_data:
        print(json_data.get("error"))
        print(json_data.get("error_description"))
        return
    task = DidaTask.parse_obj(json_data)
    # print(task.id, task.title)
    return task


def delete_task(access_token, project_id, task_id):
    url = f"https://dida365.com/open/v1/project/{project_id}/task/{task_id}"
    headers = {
        "Authorization": "Bearer " + access_token,
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Accept": "*/*",
        "Host": "dida365.com",
        "Connection": "keep-alive",
    }
    response = requests.request("DELETE", url, headers=headers)
    if response.status_code != 200:
        print(response.status_code)


def update_task(access_token, task: DidaTask):
    url = f"https://dida365.com/open/v1/task/{task.id}"
    print(url)
    task_dict = task.dict(exclude_none=True)
    payload = json.dumps(task_dict)
    print(payload)
    headers = {
        "Authorization": "Bearer " + access_token,
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Host": "dida365.com",
        "Connection": "keep-alive",
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.status_code)
    # json_data = json.loads(response.text)
    # if "error" in json_data:
    #     print(json_data.get("error"))
    #     print(json_data.get("error_description"))
    #     return
    # task = DidaTask.parse_obj(json_data)
    # # print(task.id, task.title)
    # return task


def get_task_by_id(access_token, project_id, task_id):
    url = f"https://dida365.com/open/v1/project/{project_id}/task/{task_id}"
    headers = {
        "Authorization": "Bearer " + access_token,
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Accept": "*/*",
        "Host": "dida365.com",
        "Connection": "keep-alive",
    }
    response = requests.request("GET", url, headers=headers)
    print(response.status_code)
    json_data = json.loads(response.text)
    if "error" in json_data:
        print(json_data.get("error"))
        print(json_data.get("error_description"))
        return
    task = DidaTask.parse_obj(json_data)
    # print(task.id, task.title)
    return task


def complete_task(access_token, project_id, task_id):
    url = f"https://dida365.com/open/v1/project/{project_id}/task/{task_id}/complete"
    headers = {
        "Authorization": "Bearer " + access_token,
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Accept": "*/*",
        "Host": "dida365.com",
        "Connection": "keep-alive",
    }
    response = requests.request("POST", url, headers=headers)
    print(response.status_code)


def get_project_by_id(access_token, project_id):
    url = f"https://dida365.com/open/v1/project/{project_id}/data"
    payload = {}
    headers = {
        "Authorization": "Bearer " + access_token,
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Accept": "*/*",
        "Host": "dida365.com",
        "Connection": "keep-alive",
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code != 200:
        print(response.status_code)
        return None
    # print(response.text)
    json_data = json.loads(response.text)
    if "error" in json_data:
        print(json_data.get("error"))
        print(json_data.get("error_description"))
        return
    tasks = [DidaTask.parse_obj(item) for item in json_data["tasks"]]
    # for i, task in enumerate(tasks):
    # print(i, task.id, task.title)
    return tasks


def main():
    print(__file__)
    # authorize()  # xiyF8t GLYp4T
    # get_access_token("w6sp8f")
    access_token = "3ad46d12-a0d6-454d-8ccc-e3bbce0aa943"
    # projects = get_projects(access_token)
    # current_time = arrow.now().format("YYYY-MM-DD HH:mm:ss")
    # test_task_name = f"test-task-{current_time}"
    # inbox_task = create_inbox_task(access_token, test_task_name)
    inbox_project_id = "inbox1010592152"
    inbox_tasks = get_project_by_id(access_token, inbox_project_id)
    # for task in inbox_tasks:
    # print(task.id, task.title)


if __name__ == "__main__":
    main()
