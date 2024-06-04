from playwright.sync_api import Playwright, sync_playwright, expect
import re
import eagle_client
from fish_util.src.log_util import FishLogger

logger = FishLogger(__file__)
print = logger.debug

tjd_id = eagle_client.get_folder_by_name("tjd")["id"]
if not tjd_id:
    tjd_id = eagle_client.create_folder("tjd")["id"]
print(f"tjd_id: {tjd_id}")

rw_list = [
    # {"id": 6884, "page": 3},  # 杏子
    # {"id": 6066, "page": 9},  # 唐安琪
    # {"id": 796, "page": 9},  # 樱桃酱
    {"id": 427, "page": 2},  # 赵小米
    {"id": 1577, "page": 9},  # 梦心玥
    {"id": 6229, "page": 6},  # 林星阑
    {"id": 426, "page": 1},  # 慕羽茜
    {"id": 5815, "page": 8},  # 安然anran
    {"id": 4067, "page": 3},  # 陈良玲
    {"id": 1180, "page": 2},  # Yumi-尤美
    {"id": 438, "page": 1},  # 梁莹
    {"id": 674, "page": 1},  # 佟蔓
    {"id": 451, "page": 2},  # SISY思
    {"id": 5515, "page": 4},  # 黑川
    {"id": 2438, "page": 8},  # 小热巴
    {"id": 6272, "page": 5},  # 熊小诺
    {"id": 6534, "page": 2},  # 林乐一
]


#
# rw=https://www.sqmuying.com/t/?id=6884
# zj=https://www.sqmuying.com/a/?id=72519
# img=https://tjqew5fe8ew.lt508.com/5eb7a_kmt72519-f4ed-01.jpg
def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.sqmuying.com/?action=login")
    page.get_by_placeholder("请输入用户名").click()
    page.get_by_placeholder("请输入用户名").fill("fishyer")
    page.get_by_placeholder("请输入密码").click()
    page.get_by_placeholder("请输入密码").fill("fish0113")
    page.get_by_role("button", name="登录").click()
    page.get_by_role("link", name="主页").click()
    page.get_by_role("link", name="全部图集").click()
    for info in rw_list:
        rw_id = info["id"]
        rw_page = info["page"]
        print(f"rw_info: {rw_id} {rw_page}")
        for i in range(1, rw_page + 1):
            page.goto(f"https://www.sqmuying.com/t/?id={rw_id}&page={i}")
            page.wait_for_load_state(state="load")
            rw_title = page.title()
            rw_url = page.url
            rw_folder = eagle_client.get_folder_by_name(f"{rw_id}-{rw_title}")
            if not rw_folder:
                rw_folder = eagle_client.create_sub_folder(
                    tjd_id, f"{rw_id}-{rw_title}"
                )
            rw_folder_id = rw_folder["id"]
            hezis = page.locator(".hezi>ul>li>a").all()
            print(f"rw: {len(hezis)} {rw_title} {rw_url}")
            new_page = None

            def handle_popup(event):
                nonlocal new_page
                new_page = event

            page.on("popup", handle_popup)
            for h, hezi in enumerate(hezis):
                new_page = None
                hezi.click()
                while not new_page:
                    page.wait_for_timeout(1000)
                page1 = context.pages[-1]
                zj_url = page1.url
                zj_title = page1.title()
                imgs = page1.locator(".lazy").all()
                print(f"zj-{i}-{h+1}: {len(imgs)} {zj_title} {zj_url}")
                zj_match = re.search(r"https://.*/a/\?id=(\d+)", zj_url)
                if zj_match:
                    zj_id = zj_match.group(1)
                    zj_folder = eagle_client.get_folder_by_name(f"{zj_id}-{zj_title}")
                    if zj_folder:
                        zj_folder_name = zj_folder["name"]
                        print(f"zj_folder已存在:{zj_folder_name}")
                        continue
                    if not zj_folder:
                        zj_name = f"{zj_id}-{zj_title}"
                        zj_folder = eagle_client.create_sub_folder(
                            rw_folder_id, zj_name
                        )
                    zj_folder_id = zj_folder["id"]
                    for img in imgs:
                        image_url = img.get_attribute("data-src")
                        # https://tjqew5fe8ew.lt508.com/5eb7a_kmt67095-c7001-065.jpg
                        # https://tjqew5fe8ew.lt508.com/4rgaz_sla65844-028.jpg
                        match = re.search(
                            r"https://.*/(\w+?)(\d+)(-\w+)?-(\d+)?.(\w+)", image_url
                        )
                        if match:
                            pre_token = match.group(1)
                            folder_id = match.group(2)
                            post_token = match.group(3)
                            image_id = match.group(4)
                            ext = match.group(5)
                            source = page1.url
                            file_name = f"{rw_id}-{zj_id}-{image_id}.{ext}"
                            eagle_client.add_item(
                                image_url, source, zj_folder_id, file_name
                            )
                        else:
                            print("未匹配到img_url" + image_url)
                            # 退出循环
                            break
                else:
                    print("未匹配到zj_url:" + zj_url)
    # ---------------------
    context.close()
    browser.close()


def test():
    image_url = "https://tjqew5fe8ew.lt508.com/4rgaz_sla65884-020.jpg"
    match = re.search(r"https://.*/(\w+?)(\d+)(-\w+)?-(\d+)?.(\w+)", image_url)
    if match:
        pre_token = match.group(1)
        folder_id = match.group(2)
        post_token = match.group(3)
        image_id = match.group(4)
        ext = match.group(5)
        print(f"pre_token: {pre_token}")
        print(f"folder_id: {folder_id}")
        print(f"post_token: {post_token}")
        print(f"image_id: {image_id}")
        print(f"ext: {ext}")
    else:
        print("未匹配到img_url" + image_url)


def main():
    print(__file__)
    with sync_playwright() as playwright:
        run(playwright)
    # for i in range(1, 3):
    # print(i)


if __name__ == "__main__":
    main()
    # test()
