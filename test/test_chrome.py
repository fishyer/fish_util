from playwright.sync_api import sync_playwright
import re
from fish_util.src.log_util import print
import os


def extract_session_id_from_file(file_name):
    print(f"extract_session_id_from_file: {file_name}")
    with open(file_name, "r") as file:
        for line in file:
            match = re.search(r"browser/(\w+-\w+-\w+-\w+-\w+)", line)
            if match:
                session_id = match.group(1)
                print(f"session_id: {session_id}")
                print(f"length: {len(session_id)}")
                return session_id


def test_extractxzp_session_id():
    # 使用该函数来提取 session_id
    session_id = extract_session_id_from_file(
        "/Users/yutianran/MyGithub/MyPyTest/shell/start_chrome.sh.log"
    )
    print(session_id)
    assert session_id is not None
    assert len(session_id) == 36


def test_search_google():
    with sync_playwright() as playwright:
        # session_id = "87cc44a4-1aad-4ad0-ba26-1ef49638a68d"
        session_id = extract_session_id_from_file(
            "/Users/yutianran/MyGithub/MyPyTest/shell/start_chrome.sh.log"
        )
        browser = playwright.chromium.connect_over_cdp(
            f"ws://127.0.0.1:9222/devtools/browser/{session_id}"
        )
        default_context = browser.contexts[0]
        page = default_context.pages[0]
        print(page)
        # 打开谷歌搜索Python
        page.goto("https://www.google.com/search?q=Obsidian")
        url = page.url
        print(url)
        # 等待页面加载完成
        page.wait_for_load_state()
        # 获取页面标题
        title = page.title()
        print(title)
        # 打印搜索结果
        items = page.query_selector_all("span>a:has(>h3)")
        print("搜索结果数量: " + str(len(items)))
        for item in items[:3]:
            item_link = item.get_attribute("href")
            item_title = item.query_selector(">h3").inner_text()
            print(f"{item_title} {item_link}")

        # 关闭当前页面
        # page.close()


def main():
    print(__file__)
    # os.system(f"pytest -qs {__file__}")


if __name__ == "__main__":
    main()
