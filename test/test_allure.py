import pytest
import allure
import fish_util.src.log_util as log_util

logger = log_util.FishLogger(__file__)
print = logger.debug


@pytest.fixture()
def login_fixture():
    print("前置操作-login")
    return "login_fixture_value"


def finalizer_fixture(login_fixture_value):
    print("后置操作-logout: " + login_fixture_value)


@allure.feature("功能模块a")
class TestWithLogger:
    @allure.story("子功能b")
    @allure.title("用例c")
    @allure.feature(__file__)
    def test_case1(self):
        print("用例test_case1的输出")


@allure.feature(__file__)
def test_login_fixture(login_fixture):
    print("执行测试用例-test_login_fixture")
    finalizer_fixture(login_fixture)
