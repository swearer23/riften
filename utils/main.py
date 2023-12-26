import os
from dotenv import load_dotenv

env = os.getenv('ENV')

def load_config():
  file = f'.env.{env}' if env else '.env'
  load_dotenv(file)