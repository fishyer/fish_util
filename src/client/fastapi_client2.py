from fastapi import FastAPI
import subprocess
import json
import uvicorn

import sys

print(sys.path)
import src.sysinfo_util as sysinfo_util

app = FastAPI()


@app.post("/execute/")
async def execute_command(command: str):
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    return {"stdout": stdout.decode("utf-8"), "stderr": stderr.decode("utf-8")}


@app.get("/sysinfo/")
async def get_sysinfo():
    return sysinfo_util.get_info()


@app.get("/generate_md5/")
async def generate_md5(device_id, timestamp):
    return sysinfo_util.generate_md5(device_id, timestamp)


# 在localhost:13140运行它
def main():
    print(__file__)
    # print(sysinfo_util.get_info())
    print("http://localhost:13140/docs")
    uvicorn.run(
        "fastapi_client:app", host="0.0.0.0", port=13140, reload=True, workers=1
    )


if __name__ == "__main__":
    main()
