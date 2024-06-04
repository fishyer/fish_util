from dotenv import load_dotenv
import os

# 加载.env文件
load_dotenv()

# 读取并打印环境变量
"""
build_type = "dev"
ob_vault = "MyNote"
"""

build_type = os.getenv("build_type")
print(f"build_type: {build_type}")

ob_vault = os.getenv("ob_vault")
print(f"ob_vault: {ob_vault}")


dida_access_token = os.getenv("dida_access_token")
print(f"dida_access_token: {dida_access_token}")

dida_inbox_id = os.getenv("dida_inbox_id")
print(f"dida_inbox_id: {dida_inbox_id}")

wf_session_id = os.getenv("wf_session_id")
print(f"wf_session_id: {wf_session_id}")

wf_inbox_name = os.getenv("wf_inbox_name")
print(f"wf_inbox_name: {wf_inbox_name}")

webdav_hostname = os.getenv("webdav_hostname")
print(f"webdav_hostname: {webdav_hostname}")

webdav_username = os.getenv("webdav_username")
print(f"webdav_username: {webdav_username}")

webdav_password = os.getenv("webdav_password")
print(f"webdav_password: {webdav_password}")
