import os
from dotenv import load_dotenv 

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_TOKEN = os.environ.get("API_TOKEN")