import os
import math
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
  