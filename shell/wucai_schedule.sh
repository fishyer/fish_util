#!/bin/bash
# lsof -ti:13140 | xargs kill -9
python -u "/Users/yutianran/Documents/MyPKM/script/wucai_schedule.py" 
# pm2 start pm2/wucai_schedule.sh --name wucai_schedule
# pm2 logs wucai_schedule
# pm2 flush wucai_schedule
