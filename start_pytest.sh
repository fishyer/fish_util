#!/bin/bash

# -q: 安静模式, 不输出环境信息
# -v: 丰富信息模式, 输出更详细的用例执行信息
# -s: 显示程序中的print/logging输出
# 使用相对路径，以适应不同环境
pwd
# 获取当前日期时间 YYYY-MM-DD_HH-MM-SS
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
# pytest -s -v . --clean-alluredir --alluredir=./cache/allure-results
# 不加 -sv 是为了防止自己的文件中的日志被吞，好像是会被覆盖了
pytest . --clean-alluredir --alluredir=./cache/$timestamp/allure-results

# 检查环境变量文件是否存在再复制
if [ -f environment.properties ]; then
  cp environment.properties ./cache/$timestamp/allure-results/environment.properties
else
  echo "Error: environment.properties does not exist."
fi

# 生成 Allure 报告
allure generate -c -o ./cache/$timestamp/allure-report ./cache/$timestamp/allure-results

# 优雅关闭进程
echo "Stopping process on port 11136"
pid=$(lsof -i:11136 -t)
if [ -n "$pid" ]; then
  kill $pid
  echo "Process on port 11136 stopped gracefully."
else
  echo "No process found on port 11136."
fi

# 使用 nohup 启动 Allure 服务
nohup allure open ./cache/$timestamp/allure-report -p 11136 > /dev/null 2>&1 &
echo "Allure server started on port http://localhost:11136."

# 直接查看指定时间戳的报告
# allure open ./cache/$timestamp/allure-report
# allure open ./cache/2024-05-14_15-44-26/allure-report