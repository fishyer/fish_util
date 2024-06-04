from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
from fish_util.src.log_util import FishLogger

logger = FishLogger(__file__)
print = logger.debug
print_error = logger.error


def run_command():
    command = 'python -u "/Users/yutianran/Documents/MyPKM/script/wucai_client.py"'
    print(command)
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = process.communicate()
    output_str = output.decode("utf-8")
    error_str = error.decode("utf-8")
    if output_str:
        print(output_str)
    if error_str:
        print_error(error_str)


print("start wucai_schedule")
scheduler = BlockingScheduler()
run_command()
scheduler.add_job(run_command, "cron", minute="*/10")
scheduler.start()
