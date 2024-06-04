#!/bin/bash

pkill -f "uvicorn fastapi_client:app"
lsof -ti:18001 | xargs kill
sleep 3
cd /Users/yutianran/Documents/MyCode/MyScript/fish_script/client
echo "Starting FastAPI server at http://localhost:18001/docs"
nohup uvicorn fastapi_client:app --host 0.0.0.0 --port 18001 --reload >> "$0.log" 2>&1 &