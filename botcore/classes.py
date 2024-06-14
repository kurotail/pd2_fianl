import discord
from discord.ext import commands

class Cog_Extension(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

class BoardData():
    def __init__(self, board_data: dict) -> None:
        self.last_image_msgID: int = None
        self.board: list[list[int]] = board_data.get("board")
        self.user_ans_board: list[list[int]] = board_data.get("user_ans_board")
        self.hint_board: list[list[int]] = board_data.get("hint_board")
        self.ans_board: list[list[int]] = board_data.get("ans_board")
        self.difficulty: int = board_data.get("difficulty")
        self.x: int = board_data.get("x")
        self.y: int = board_data.get("y")