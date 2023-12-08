from enum import Enum
import click

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

intervals = [
  # '1s',
  # '3s',
  # '5s',
  # '15s',
  # '30s',
  '1m',
  '3m',
  '5m',
  '15m',
  '30m',
  '1h',
  '2h',
  '4h',
  '6h',
  '8h',
  '12h',
  '1d',
  # '3d',
  # '1w',
  # '1M',
]

@click.command()
def cli_set_interval():
  """示例程序：单选交互"""
  choice = click.prompt(
      f'请选择一个选项：',
      type=click.Choice(intervals),
      show_choices=True# 不显示可选项，由提示信息呈现
  )

  return choice