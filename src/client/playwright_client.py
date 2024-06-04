from playwright.sync_api import Playwright, sync_playwright 
import subprocess

#输入Chrome浏览器所在路径
chrome_path ="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
debugging_port = "--remote-debugging-port=9222"

command = f"{chrome_path} {debugging_port}"
subprocess.Popen(command, shell=True)

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.connect_over_cdp(("http://localhost:9222"))
    context = browser.contexts[0]
    page = context.new_page()
    # 打开谷歌搜索Python
    page.goto("https://www.google.com/search?q=Python")
    # 等待页面加载完成
    page.wait_for_load_state()
    # 打印前10条搜索结果
    for i in range(10):
        print(page.query_selector(f"#rso > div:nth-child({i+1}) > div > a").inner_text())
    # 关闭浏览器
    # browser.close()

with sync_playwright() as playwright:
    run(playwright)


from playwright.sync_api import sync_playwright,Playwright
from script.util.log_util import logger

print=logger.info

def run(playwright: Playwright):
    browser = playwright.chromium.connect_over_cdp("ws://127.0.0.1:9222/devtools/browser/0339b847-bb4e-4b58-95d0-462f428a96bf")
    default_context = browser.contexts[0]
    page = default_context.pages[0]
    print(page)
    # 打开谷歌搜索Python
    page.goto("https://www.google.com/search?q=Obsidian")
    url=page.url
    print(url)
    # 等待页面加载完成
    page.wait_for_load_state()
    # 获取页面标题
    title = page.title()
    print(title)
    # 打印搜索结果
    items=page.query_selector_all(f"span>a:has(>h3)")
    print("搜索结果数量: "+str(len(items)))
    for item in items[:3]:
        item_link=item.get_attribute("href")
        item_title=item.query_selector(">h3").inner_text()
        print(f"{item_title} {item_link}")

    # 关闭当前页面
    # page.close()    

with sync_playwright() as playwright:
    run(playwright)