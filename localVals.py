import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = 447012513209516052
SUDOKU_URL = "https://sudoku-online.com/"
BOARD_DATA_PATH = "./board_data.pickle"
CORRECT_ANI_PATH = "./assets/ani/correct.gif"