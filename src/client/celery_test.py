import celery_client
import jina_client
import devonthink_client
from fish_util.src.log_util import FishLogger
from fish_util.src import file_util
from fish_util.util import time_util

logger = FishLogger(__file__)
print = logger.debug


def test_add():
    task = celery_client.add.delay(2, 4)
    print(f"task: {task}")
    result = task.get()
    print(f"result: {result}")


def test_url2md():
    url = "https://mp.weixin.qq.com/s/IXcxlzvW-SURGOHEdUDrbg"
    result = celery_client.url2md.delay(url)
    print(f"task: {result}")
    title, md_content = result.get()
    print(f"title: {title}")

    # note_dir = time_util.get_time_dir("note/clipper")
    # print(f"note_dir: {note_dir}")
    # md_path = f"{note_dir}/{jina_client.sanitize_title_for_filename(title)}.md"
    # print(f"md_path: {md_path}")
    # file_util.write_file(md_path, md_content)


def main():
    print(__file__)
    test_add()
    test_url2md()


if __name__ == "__main__":
    main()
