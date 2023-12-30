import os
import smtplib
import math
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

env = os.getenv('ENV')

def load_config():
  file = f'.env.{env}' if env else None
  load_dotenv(file)

def floor_float(number, precision):
  multiplier = 10 ** precision
  return math.floor(number * multiplier) / multiplier

def effective_precision(decimal_str):
  decimal_str = decimal_str.lstrip('0')

  # 检查字符串是否表示小数
  if '.' in decimal_str:
    decimal_part = decimal_str.split('.')[1]  # 获取小数部分
    return len(decimal_part.rstrip('0'))  # 去掉小数部分末尾的零并计算长度
  else:
    return 0
  
def send_mail(title, content, mimetype='plain'):
  # 设置发件人和收件人邮箱
  sender_email = os.environ.get('EMAIL_ACCOUNT')
  receiver_email = os.environ.get('EMAIL_ACCOUNT')

  # 创建邮件内容
  message = MIMEMultipart()
  message['From'] = sender_email
  message['To'] = receiver_email
  message['Subject'] = title

  # 邮件正文内容
  body = content
  message.attach(MIMEText(body, mimetype))

  # 连接到 SMTP 服务器
  with smtplib.SMTP_SSL('smtp.163.com', 465) as smtp_server:
      # smtp_server.starttls()  # 开启 TLS 加密（如果服务器支持）
      smtp_server.login(sender_email, os.environ.get('EMAIL_PASSWORD'))

      # 发送邮件
      smtp_server.send_message(message)

  print("邮件发送成功")