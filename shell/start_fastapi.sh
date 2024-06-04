#!/bin/bash

# 优雅关闭进程
echo "Stopping process on port 28001"
pid=$(lsof -i:28001 -t)
if [ -n "$pid" ]; then
  kill -9 $pid
  echo "Process on port 11136 stopped gracefully."
else
  echo "No process found on port 28001."
fi


# Start the FastAPI server
cd /Users/yutianran/MyGithub/MyPyTest/client
echo "Starting FastAPI server at http://localhost:28001/docs"
nohup uvicorn fastapi_client:app --host 0.0.0.0 --port 28001 &