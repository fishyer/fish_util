#!/bin/bash
lsof -ti:13140 | xargs kill -9
python -u "/Users/yutianran/Documents/MyPKM/script/fastapi_client.py"
# pm2 start pm2/fastapi_client.sh --name fastapi_client
# pm2 start /Users/yutianran/Documents/MyPKM/pm2/FastApi-Command.sh --name FastApi-Command
# http://localhost:13140/docs