#!/bin/bash

pkill -f "celery"
cd /Users/yutianran/Documents/MyCode/MyScript/fish_script/client
echo "Starting Celery server"
nohup celery -A celery_client worker --loglevel=warning >> "$0.log" 2>&1 &