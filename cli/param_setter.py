from enum import Enum
import click
from common import intervals

class MODE(Enum):
  UPDATE = 1
  TEST = 2

@click.command()
def cli_set_mode():
  options =[
    '更新数据',
    '测试数据'
  ]
  options_str = '\n'.join([f'{i}. {option}' for i, option in enumerate(options, 1)])
  """示例程序：单选交互"""
  choice = click.prompt(
      f'请选择一个选项：\n{options_str} \n你的选择',
      type=click.Choice([str(i) for i in range(1, len(options) + 1)]),
      show_choices=False# 不显示可选项，由提示信息呈现
  )

  return int(choice)

@click.command()
def cli_set_interval():
  """示例程序：单选交互"""
  choice = click.prompt(
      f'请选择一个选项：',
      type=click.Choice(intervals),
      show_choices=True# 不显示可选项，由提示信息呈现
  )

  return choice