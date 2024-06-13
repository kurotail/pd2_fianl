import discord
from discord.ext import commands

class Cog_Extension(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

class BoardData():
    def __init__(self, board_data: dict) -> None:
        self.board = board_data.get("board")
        self.user_ans_board = board_data.get("user_ans_board")
        self.hint_board = board_data.get("hint_board")
        self.ans_board = board_data.get("ans_board")
        self.difficulty = board_data.get("difficulty")
        self.x = board_data.get("x")
        self.y = board_data.get("y")