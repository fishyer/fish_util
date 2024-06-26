# 我的Python工具库

github地址：[fishyer/fish_util](https://github.com/fishyer/fish_util )
pypi地址：[fish_util](https://pypi.org/project/fish_util/)

## 介绍

这是我自己编写的一些Python工具库，包括：
- log_util
- decorator_util：包括trace_exception、trace_time、trace_args、trace_retry、trace_validate等装饰器
- file_util
- yaml_util
- json_util
- redis_util
- mysql_util
- mongo_util
- oss_util
- date_util
- string_util
- re_util
- collections_util
- function_util

## 安装

```
pip install fish_util
```

## 使用示例

```python
from fish_util.src.log_util import logger
import fish_util.src.decorator_util as decorator_util

logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")


@decorator_util.trace_exception
@decorator_util.trace_time
@decorator_util.trace_args
@decorator_util.trace_retry(max_attempts=2, delay=1)
@decorator_util.trace_validate(
    lambda username: len(username) > 0, lambda password: len(password) > 0
)
def login(username, password):
    if username == "admin" and password == "123456":
        return True
    else:
        return False


def main():
    print(__file__)
    print(login("admin", "123456"))
    print(login("", "123456"))


if __name__ == "__main__":
    main()
```

## 输出结果

![](https://yupic.oss-cn-shanghai.aliyuncs.com/202405141752940.png)