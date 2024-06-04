import sys
import logging

# 创建Logger对象
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # 设置日志记录级别为INFO

# 创建FileHandler用于输出到文件
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)  # 设置文件日志记录级别为DEBUG

# 创建StreamHandler用于输出到控制台
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # 设置控制台日志记录级别为INFO

# 设置日志记录格式
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 将Handler添加到Logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 定义日志输出函数
print = logger.debug
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
