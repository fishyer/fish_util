class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def login(self, username, password):
        if username == self.username and password == self.password:
            print("登录成功！")
            return True
        else:
            print("用户名或密码错误。")
            return False


# 示例
if __name__ == "__main__":
    user = User("example_user", "example_password")
    user.login("example_user", "example_password")  # 应该打印出 "登录成功！"
    user.login("wrong_user", "example_password")  # 应该打印出 "用户名或密码错误。"
