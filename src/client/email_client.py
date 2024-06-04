import smtplib
from email.mime.text import MIMEText
from fish_util.src.log_util import FishLogger

logger = FishLogger(__file__)
print = logger.debug


def send_email(content):
    # 设置服务器所需信息
    mail_host = "smtp.qq.com"
    mail_user = "630709658@qq.com"
    mail_pass = "oygptpnetvqdbece"
    # 邮件发送方邮箱地址
    sender = "fishyer@foxmail.com"
    receivers = ["630709658@qq.com"]
    # 邮件内容设置
    # content = "this is a test mail content"
    message = MIMEText(content, "plain", "utf-8")
    message["Subject"] = "MarkSearch邮件通知"
    message["From"] = sender
    message["To"] = receivers[0]
    # 登录并发送邮件
    try:
        server = smtplib.SMTP_SSL(mail_host, 465)
        server.login(mail_user, mail_pass)
        server.sendmail(sender, receivers, message.as_string())
        server.quit()
        print("success")
        return True
    except smtplib.SMTPException as e:
        logger.error(e)
        return False


def main():
    print(__file__)
    send_email()


if __name__ == "__main__":
    main()
