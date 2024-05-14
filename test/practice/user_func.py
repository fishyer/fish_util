from dataclasses import dataclass, field


@dataclass
class User:
    username: str
    password: str


@dataclass
class GlobalVariable:
    key1: str
    key2: str
    key3: str
    # 延迟属性
    total_cost: float = field(init=False)

    def __post_init__(self):
        self.total_cost = self.unit_price * self.quantity_on_hand


def login(gv: GlobalVariable, self: User, username, password):
    if username == self.username and password == self.password:
        print("登录成功！")
        return True
    else:
        print("用户名或密码错误。")
        return False


def main():
    print(__file__)
    gv = GlobalVariable("value1", "value2", "value3")
    user = User("example_user", "example_password")
    login(gv, user, "example_user", "example_password")  # 应该打印出 "登录成功！"
    login(gv, user, "wrong_user", "example_password")  # 应该打印出 "用户名或密码错误。"


if __name__ == "__main__":
    main()
