#!/bin/bash

# 获取当前脚本文件名
echo "当前脚本文件: $0"

# 检查是否存在 Chrome 进程
if pgrep "Google Chrome" > /dev/null; then
    echo "Chrome 进程已经在运行"
    # 杀死所有 Chrome 进程
    killall -9 "Google Chrome"
fi
echo "开始启动 Chrome"
# 后台运行 Chrome 命令，并将输出重定向到日志文件
nohup sh "/Users/yutianran/MyGithub/MyPyTest/shell/chrome_command.sh" > "$0.log" 2>&1 &
echo "成功启动 Chrome"