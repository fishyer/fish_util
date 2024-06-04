import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # 判断是否是新建了md文件
        if not event.is_directory and event.src_path.endswith('.md'):
            print(f'File {event.src_path} has been modified')
            subprocess.run(["python", "-u", "/Users/yutianran/Documents/MyPKM/wucai_daily_content.py"])

if __name__ == "__main__":
    path = "/Users/yutianran/Documents/MyPKM/MyNote/001-Inbox/EzWucai"
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        count = 0
        while True:
            time.sleep(10)
            count += 1
            print(f"Watching: {path} for 10 seconds. Count: {count}")
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
