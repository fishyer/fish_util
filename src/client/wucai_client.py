import re
import frontmatter
import os
import arrow
import shutil
from pathlib import Path
import os
import fish_util.src.file_util as file_util
from fish_util.src.log_util import print
import requests
import json
import fish_script.client.eagle_client as eagle_client
from fish_util.src.yaml_util import YamlLoader

marksearch_folder_id = "LW8LECFYUG93K"

# cache_file = "/Users/yutianran/MyGithub/MyPyTest/cache/wucai.yaml"
# yml = YamlLoader(cache_file)
# caches = yml.file_load()
# wucai_paths = caches["wucai_paths"]


def test_hello():
    print("hello world")


def seconds_to_hhmmss(seconds):
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def update_daily_notes(file_path, new_notes):
    # 文件不存在，或re搜不到## 今日速记部分
    if not os.path.exists(file_path) or not re.search(r"## 今日速记\n\n", file_path):
        # print(f"日志文件不存在：{file_path}")
        # 创建文件
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"## 今日速记\n\n")
            file.write(new_notes)
            file.write("\n")
        return

    # 更新文件
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    updated_content = re.sub(
        r"(## 今日速记\n\n)(.*?)(?=##|\Z)",
        r"\1" + new_notes + "\n",
        content,
        flags=re.DOTALL,
    )

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_content)
        # print(f"更新日志文件：{file_path}")


def update_highlighted_underline(file_path, new_notes):
    # 文件不存在，或re搜不到## 今日高亮部分
    if not os.path.exists(file_path) or not re.search(r"## 今日高亮\n\n", file_path):
        # print(f"高亮文件不存在：{file_path}")
        # 创建文件
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"## 今日高亮\n\n")
            file.write(new_notes)
            file.write("\n")
        return

    # 更新文件
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    updated_content = re.sub(
        r"(## 今日高亮\n\n)(.*?)(?=##|\Z)",
        r"\1" + new_notes + "\n",
        content,
        flags=re.DOTALL,
    )

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_content)
        # print(f"更新高亮文件：{file_path}")


def update_bookmark(file_path, new_notes):
    # 文件不存在，或re搜不到## 今日待读
    if not os.path.exists(file_path) or not re.search(r"## 今日书签\n\n", file_path):
        # print(f"待读文件不存在：{file_path}")
        # 创建文件
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"## 今日书签\n\n")
            file.write(new_notes)
            file.write("\n")
        return

    # 更新文件
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    updated_content = re.sub(
        r"(## 今日书签\n\n)(.*?)(?=##|\Z)",
        r"\1" + new_notes + "\n",
        content,
        flags=re.DOTALL,
    )

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_content)
        # print(f"更新待读文件：{file_path}")


def update_readlater(file_path, new_notes):
    # 文件不存在，或re搜不到## 今日待读
    if not os.path.exists(file_path) or not re.search(r"## 今日待读\n\n", file_path):
        # print(f"待读文件不存在：{file_path}")
        # 创建文件
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"## 今日待读\n\n")
            file.write(new_notes)
            file.write("\n")
        return

    # 更新文件
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    updated_content = re.sub(
        r"(## 今日待读\n\n)(.*?)(?=##|\Z)",
        r"\1" + new_notes + "\n",
        content,
        flags=re.DOTALL,
    )

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_content)
        # print(f"更新待读文件：{file_path}")


def extract_daily_notes(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        # 使用正则表达式提取今日速记部分
        daily_notes = re.search(r"## 每日速记\n(.*?)(?=##|\Z)", content, re.DOTALL)
        if daily_notes:
            # 提取每个列表节点
            notes_list = re.findall(
                r"- (.*?)(?=\n-|\Z)", daily_notes.group(1), re.DOTALL
            )
            return notes_list
        else:
            return []


def extract_highlighted_underline(file_path):
    content = file_util.read_file(file_path)
    return extract_highlighted_underline_by_content(content)


def extract_highlighted_underline_by_content(content):
    highlighted_list = []
    highlighted_underline_blocks = re.findall(
        r"## 高亮划线\n(.*?)\n(?=##|\Z)", content, re.DOTALL
    )
    if highlighted_underline_blocks:
        for block in highlighted_underline_blocks:
            items = re.findall(r"\n> (.*?)(?=\n\n|\Z)", block, re.DOTALL)
            if items:
                for item in items:
                    highlighted_list.append(item)
    return highlighted_list


def extract_full_text_clipping(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        # 使用正则表达式提取全文剪藏部分
        full_text_clipping = re.search(
            r"## 全文剪藏\n\n(.*?)(?=!\[cover_image\]|\Z)", content, re.DOTALL
        )
        if full_text_clipping:
            return full_text_clipping.group(1)
        else:
            return ""


def preprocess_frontmatter(file_path):
    input_content = file_util.read_file(file_path)
    # 定义正则表达式匹配 Front Matter 部分
    frontmatter_pattern = r"---\n(.*?)\n---\n"

    # 使用正则表达式匹配 Front Matter 部分
    match = re.search(frontmatter_pattern, input_content, re.DOTALL)

    if match:
        frontmatter_content = match.group(1)
        # 逐行处理 Front Matter 部分内容
        processed_lines = []
        is_processed = False
        for line in frontmatter_content.split("\n"):
            if line.startswith("原始标题:"):
                processed_line = (
                    line.replace("[", "")
                    .replace("]", "")
                    .replace("/", "")
                    .replace('"', "")
                )
                if line != processed_line:
                    processed_lines.append(processed_line)
                    is_processed = True
            else:
                processed_lines.append(line)
        processed_frontmatter = "\n".join(processed_lines)
        # 将处理好的保存到文件里面
        if is_processed:
            output_content = input_content.replace(
                frontmatter_content, processed_frontmatter
            )
            file_util.write_file(file_path, output_content)
            return output_content
        else:
            return input_content
    else:
        return input_content


def extract_frontmatter_properties(file_path):
    # print(f"extract_frontmatter_properties: {file_path}")
    # 预处理 Front Matter 部分
    file_content = preprocess_frontmatter(file_path)
    # 加载 Front Matter 部分
    post = frontmatter.loads(file_content)
    metadata = post.metadata
    return metadata


def check_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        print(f"文件行数: {len(lines)} 文件名: {file_path}")


def get_hhmmss(s):
    # 匹配字符串中的hhmmss时间
    match = re.search(r"\d{2}:\d{2}:\d{2}", s)
    if match:
        return match.group(0)
    else:
        return ""


def extract_items_from_md(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    pattern = re.compile(
        r"(- \d{2}:\d{2}:\d{2} .*?)(?=- \d{2}:\d{2}:\d{2} |\Z)", re.DOTALL
    )
    items = re.findall(pattern, content)
    return items


def check_link(note):
    matched = re.search(r"^\d{2}:\d{2}:\d{2} \[(.*?)\]\((.*?)\)$", note.strip())
    if matched:
        name = matched.group(1).strip()
        url = matched.group(2).strip()
        return name, url
    else:
        return None


def get_wucai(file_path):
    daily_content = []
    highlight_content = []
    readlater_content = []
    bookmark_content = []
    ## 元数据
    fm = extract_frontmatter_properties(file_path)
    createat_ts = arrow.get(int(fm["createat_ts"]), tzinfo="Asia/Shanghai")
    hhmmss = createat_ts.format("HH:mm:ss")
    title = fm["原始标题"]
    link = fm["原始链接"]
    note_count = fm["高亮数量"]
    if "Daily Note" in title:  # 今日速记
        daily_content.append(f"\n\n- {hhmmss} [{title}]({link} )\n")
        ## 今日速记
        notes = extract_daily_notes(file_path)
        # print(f'len(notes): {len(notes)}')
        for note in notes:
            # 包含#今日书签或者符合正则的[]()样式
            if "#今日书签" in note or check_link(note):
                bookmark_content.append("\n- " + note.strip() + "\n")
            else:
                daily_content.append("\n- " + note.strip() + "\n")
    else:
        # 网页高亮
        if note_count > 0:
            highlight_content.append(
                f"\n\n- {hhmmss} {note_count} [{title}]({link} )\n"
            )
            # 今日高亮
            highlighted_underline = extract_highlighted_underline(file_path)
            # print(f'len(highlighted_underline): {len(highlighted_underline)}')
            for item in highlighted_underline:
                # 检查是否包含图片链接，如果包含，则添加到Eagle库
                if re.search(r"\!\[.*?\]\(.*?\)", item):
                    search_result = re.search(r"\!\[(.*?)\]\((.*?)\)", item)
                    image_name = search_result[1]
                    image_url = search_result[2]
                    eagle_client.add_item_with_cache(
                        image_url, link, marksearch_folder_id, title + "-" + image_name
                    )
                highlight_content.append(
                    "    - " + item.strip().replace("\n> ", "\n        - ") + "\n"
                )
        else:
            # 今日待读
            readlater_content.append(f"\n\n- {hhmmss} [{title}]({link} )\n")

    ## 全文剪藏
    # full_text_clipping = extract_full_text_clipping(file_path)
    # md_content.append(full_text_clipping.strip())

    return daily_content, highlight_content, readlater_content, bookmark_content


daily_cache = {}
highlight_cache = {}
readlater_cache = {}
bookmark_cache = {}

# def safe_get(dict_obj, key, default=None):
#     """
#     从字典中安全获取值
#     :param dict_obj: 目标字典
#     :param key: 键名
#     :param default: 默认值（可选）
#     :return: 如果键存在，则返回对应的值；反之，返回默认值
#     """
#     return dict_obj.get(key, default)


def write_daily(md_content, output_file_path):
    # 先获取原先的内容，合并新内容
    if os.path.exists(output_file_path):
        items = extract_items_from_md(output_file_path)
        md_content = items + md_content
    # md_content列表，按照字符串中的hhmmss时间顺序排列: - 10:41:35 测试文本
    md_content = sorted(md_content, key=lambda x: get_hhmmss(x), reverse=True)
    # 写入文件
    print(f"len(md_content): {len(md_content)}")
    with open(output_file_path, "w") as f:
        for item in md_content:
            f.write(item)
        print(f"写入日志文件：{output_file_path}")


def move_md_files(source_dir, destination_dir):
    # # 获取source_dir下所有的md文件
    # md_files = [f for f in os.listdir(source_dir) if f.endswith('.md')]

    # for file in md_files:
    #     # 构建文件的完整路径
    #     source_file = os.path.join(source_dir, file)
    #     destination_file = os.path.join(destination_dir, file)
    #     # 移动文件
    #     shutil.move(source_file, destination_file)
    #     print(f"移动文件：{source_file} -> {destination_file}")
    # 获取当前时间的字符串表示，形如'YYYY-MM-DD'
    current = arrow.now().strftime("%Y-%m-%d_%H-%M-%S")

    # 构建带有时间后缀的目标文件夹路径
    destination_dir_with_date = os.path.join(
        destination_dir, f"{current}_{os.path.basename(source_dir)}"
    )

    # 移动source_dir文件夹到destination_dir下
    shutil.move(source_dir, destination_dir_with_date)
    print(f"移动文件夹：{source_dir} -> {destination_dir_with_date}")

    # 创建新的source_dir文件夹
    os.mkdir(source_dir)
    print(f"创建文件夹：{source_dir}")


def generate_daily_logs(root_folder, output_folder):
    # 定义匹配文件名的正则表达式
    file_name_regex = r"\d{6}-(.*?)-[A-Z0-9]{7}\.md"

    # 遍历日期
    start_date = arrow.get("2024-05-01")
    # end_date = arrow.get('2023-05-01')
    end_date = arrow.now()
    current_date = start_date

    while current_date <= end_date:
        folder_path = os.path.join(root_folder, current_date.strftime("%Y/%m/%d"))
        output_file_path = os.path.join(
            output_folder, current_date.strftime("%Y/%m/%Y-%m-%d.md")
        )
        # print(f"folder_path: {folder_path}")
        # print(f"output_file_path: {output_file_path}")
        # 检查folder_path是否存在，不存在则跳过
        if not os.path.exists(folder_path):
            print(f"folder_path not exists: {folder_path}")
            current_date = current_date.shift(days=1)  # 使用Arrow的日期偏移方法
            continue
        # 检查output_file_path是否存在，不存在则创建
        output_file_path_obj = Path(output_file_path)
        if not output_file_path_obj.exists():
            output_file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            output_file_path_obj.touch()
            print(f"创建文件：{output_file_path}")

        # 获取文件夹中所有md文件的文件名
        md_files = [f for f in os.listdir(folder_path) if re.match(file_name_regex, f)]
        # print(f"len(md_files) for {current_date.format('YYYY-MM-DD')}: {len(md_files)}")

        # 倒序排序
        md_files = sorted(md_files, reverse=False)

        # 逐个读取文件，并打印文件名和总行数
        for file_name in md_files:
            file_path = os.path.join(folder_path, file_name)
            # 检查当前文件是否需要跳过
            if check_need_skip_collect(file_path):
                continue
            # check_file(file_path)
            # 加入缓存
            # wucai_paths.append(file_path)
            # 获取五彩内容
            daily_content, highlight_content, readlater_content, bookmark_content = (
                get_wucai(file_path)
            )
            # 更新缓存
            if output_file_path in daily_cache:
                daily_cache[output_file_path].extend(daily_content)
            else:
                daily_cache[output_file_path] = daily_content
            if output_file_path in highlight_cache:
                highlight_cache[output_file_path].extend(highlight_content)
            else:
                highlight_cache[output_file_path] = highlight_content
            if output_file_path in readlater_cache:
                readlater_cache[output_file_path].extend(readlater_content)
            else:
                readlater_cache[output_file_path] = readlater_content
            if output_file_path in bookmark_cache:
                bookmark_cache[output_file_path].extend(bookmark_content)
            else:
                bookmark_cache[output_file_path] = bookmark_content

        # 输出到聚合日志
        # 记得要先判断:
        # 1.是否在缓存里面已经生成过了
        # 2.是否是今天的日志，如果是今天的日志，则不管缓存里面是否已经生成过了，都要重新生成
        if check_need_generate_daily(output_file_path):
            daily_content = daily_cache.get(output_file_path, [])
            highlight_content = highlight_cache.get(output_file_path, [])
            readlater_content = readlater_cache.get(output_file_path, [])
            bookmark_content = bookmark_cache.get(output_file_path, [])
            # write_daily(wucai, output_file_path)
            # 先将之前的文件内容清空
            file_util.clear_file(output_file_path)
            update_daily_notes(output_file_path, "".join(daily_content))
            update_bookmark(output_file_path, "".join(bookmark_content))
            update_highlighted_underline(output_file_path, "".join(highlight_content))
            update_readlater(output_file_path, "".join(readlater_content))

            # 打印一条数量统计信息
            print(
                f"生成日志: {Path(output_file_path).name} daily={len(daily_content)} bookmark={len(bookmark_content)} highlight={len(highlight_content)} readlater={len(readlater_content)}"
            )
            # wucai_paths.append(output_file_path)

        # 增加一天
        current_date = current_date.shift(days=1)  # 使用Arrow的日期偏移方法
    # 保存缓存
    # caches["wucai_paths"] = wucai_paths
    # last_time = arrow.now().format("YYYY-MM-DD HH:mm:ss")
    # caches["last_time"] = last_time
    # yml.file_dump(caches)


# 是否需要跳过收集数据
def check_need_skip_collect(file_path):
    if force_update:
        return False
    # /Users/yutianran/Documents/MyPKM/note/wucai/2024/05/16/130549-DooTask：最受欢迎的开源项目协作工具 - 掘金-H8C6KM5.md
    # /Users/yutianran/Documents/MyPKM/note/daily/2024/05/2024-05-14.md
    now_date_folder_path = arrow.now().format("YYYY/MM/DD")
    # 如果不是今天的数据，则跳过收集阶段
    if now_date_folder_path not in file_path and force_update == False:
        return True
    return False


force_update = False


# 是否需要输出日志
def check_need_generate_daily(output_file_path):
    if force_update:
        return True
    now_date = arrow.now().format("YYYY-MM-DD")
    # 如果是今天的数据，则重新生成
    if now_date in output_file_path:
        # print(f"文件 {output_file_path} 是今天的日志，需要重新生成")
        return True
    return False


def main():
    root_folder = "/Users/yutianran/Documents/MyNote/wucai"
    output_folder = "/Users/yutianran/Documents/MyNote/daily"
    # move_md_files('/Users/yutianran/Documents/MyNote/daily', '/Users/yutianran/MyCache/cache-daily')
    generate_daily_logs(root_folder, output_folder)
    print("done!!!")


if __name__ == "__main__":
    print(__file__)
    main()

    # test_path="/Users/yutianran/Documents/MyPKM/note/001-Inbox/EzWucai/2024/05/09/215717-[内部分享资料] 一文带你入门MongoDB-H852C55.md"
    # extract_frontmatter_properties(test_path)

# hhmmss=get_hhmmss("- 10:41:35 p@31415926#q #今日速记 ")
# print(hhmmss)
