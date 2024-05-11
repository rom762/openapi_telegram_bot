from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('OPENAI_TOKEN')
telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

