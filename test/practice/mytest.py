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
