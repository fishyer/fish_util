import pytest
import allure
import sys

from fish_util.src import log_util

# from ..src import log_util


@allure.feature(__file__)
def test():
    print(__file__)
    logger = log_util.FishLogger()
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.print(logger.msg_wrapper("print", "print", caller_level=0))
    logger.write("write")
    logger.record("record", "record", caller_level=1)
    logger.print(__file__)


if __name__ == "__main__":
    test()
