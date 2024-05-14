import os
import fnmatch

black_pattern_list = [
    "**/cache",
    "**/log",
    "**/__pycache__",
    "**/.pytest_cache",
    "**/.vscode",
    "**/.git",
    "**/*.log",
]


def is_black_path(path):
    for pattern in black_pattern_list:
        if fnmatch.fnmatch(path, pattern):
            # print(f"ignore path: {path} by pattern: {pattern}")
            return True
    return False


def print_directory_contents(path, dirs=[], files=[], levle=0):
    # 检查路径是否存在
    if not os.path.exists(path):
        # print("路径不存在:", path)
        return
    print("    " * levle + "- ", path)
    for child in os.listdir(path):
        child_path = os.path.join(path, child)
        if is_black_path(child_path):
            continue
        # 先收集
        if os.path.isdir(child_path):
            dirs.append(child_path)
        elif os.path.isfile(child_path):
            files.append(child_path)
        else:
            pass  # 忽略其他类型
            # print("其他:", child_path)
    # 打印目录结构
    levle += 1
    for i in dirs:
        name = os.path.basename(i)
        print_directory_contents(name, [], [], levle)
    for i in files:
        name = os.path.basename(i)
        print("    " * levle + "- ", name)


def main():
    print(__file__)
    print_directory_contents("/Users/yutianran/MyGithub/fish_util")


if __name__ == "__main__":
    main()
