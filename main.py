#discord bot "sudokun"

import discord
import discord.context_managers
from discord.ext import commands
from discord import app_commands
from sudoku.sudoku import SudokuResult
from crawler import SudokuCrawler
from botcore import descript, userBoards
from botcore.botViews import SudokuView, ConfirmView
from localVals import *
import asyncio

class Bot(commands.Bot):

    def __init__(self) -> None:
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="sudoku!",
            intents=intents,
            help_command=None,
            activity=discord.Game(name="/start_sudoku")
        )

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))
        self.tree.on_error = self.on_app_command_error
        print(f"Now login user: {self.user}.")

    async def on_app_command_error(self, interaction: discord.Integration, error: app_commands.errors) -> None:
        if isinstance(error, app_commands.errors.CommandOnCooldown):
            await interaction.response.send_message(
                f"冷卻中 (Cooldown): {round(error.retry_after, 2)}s", 
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"發生意料之外的錯誤 (Unexpected error):\n {error}s", 
                ephemeral=True
            )
    
bot = Bot()
sudoku_crawler = SudokuCrawler()

@bot.tree.command(name="cheat", description=descript.cheat)
@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
async def cheat(interaction: discord.Integration) -> None:
    await interaction.response.defer(ephemeral=True)
    await interaction.edit_original_response(content="正在讀取資料 <a:loading_dots:1093174815545888851>")
    log_channel = bot.get_channel(1250654346861875200)
    
    if userBoards.have_board(interaction.user.id) == False:
        await interaction.edit_original_response(content="您沒有遊戲紀錄，請使用 /new_sudoku 來開啟新遊戲")
        return
    
    board_data = userBoards.get_user_board(interaction.user.id)
    for y in range(9):
        for x in range(9):
            if board_data.board[y][x] == 0:
                board_data.user_ans_board[y][x] = board_data.ans_board[y][x]
    userBoards.set_user_board(interaction.user.id, board_data)
    
    await interaction.edit_original_response(
        content = await userBoards.get_board_msg(interaction.user.id, log_channel),
        view = SudokuView(interaction.user.id, interaction, log_channel)
    )

@bot.tree.command(name="start_sudoku", description=descript.start_sudoku)
@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
async def start_sudoku(interaction: discord.Integration) -> None:
    await interaction.response.defer(ephemeral=True)
    await interaction.edit_original_response(content="正在讀取資料 <a:loading_dots:1093174815545888851>")
    log_channel = bot.get_channel(1250654346861875200)
    
    if userBoards.have_board(interaction.user.id) == False:
        await interaction.edit_original_response(content="您沒有遊戲紀錄，請使用 /new_sudoku 來開啟新遊戲")
        return
    
    await interaction.edit_original_response(
        content = await userBoards.get_board_msg(interaction.user.id, log_channel),
        view = SudokuView(interaction.user.id, interaction, log_channel)
    )

@bot.tree.command(name="new_sudoku", description=descript.new_sudoku)
@app_commands.describe(difficulty = descript.new_sudoku_difficulty)
@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
async def new_sudoku(interaction: discord.Integration, difficulty: int) -> None:
    await interaction.response.defer(ephemeral=True)
    await interaction.edit_original_response(content="正在爬取題目 <a:loading_dots:1093174815545888851>")
    log_channel = bot.get_channel(1250654346861875200)
    last_board_img = None
    if userBoards.have_board(interaction.user.id):
        
        confirm_view = ConfirmView(interaction)
        await interaction.edit_original_response(
            content = "您已經有一場遊戲紀錄了，您是否要開始新的遊戲？",
            view = confirm_view
        )
        await confirm_view.wait() #等待回復是否開啟新遊戲
        
        if confirm_view.value == False: #不開啟新遊戲
            
            confirm_view = ConfirmView(interaction)
            await interaction.edit_original_response(
                content = "是否繼續上次的遊戲？",
                view = confirm_view   
            )
            await confirm_view.wait() #等待回復是否繼續上次遊戲
            
            if confirm_view.value: #繼續上次遊戲
                await interaction.edit_original_response(
                    content = await userBoards.get_board_msg(interaction.user.id, log_channel),
                    view = SudokuView(interaction.user.id, interaction, log_channel)
                )
                return
            
        if confirm_view.value != True: #按下取消或不繼續上次遊戲
            await interaction.delete_original_response()
            return

        last_board_img = userBoards.get_user_board(interaction.user.id).last_image_msgID
    
    while True:
        await interaction.edit_original_response(content="正在爬取題目 <a:loading_dots:1093174815545888851>")
        try:
            board = await sudoku_crawler.crawlBoard(difficulty)
        except ValueError:
            await interaction.edit_original_response(content="難度必須在 0~3 之間")
            return
        
        await interaction.edit_original_response(content="正在分析題目 <a:loading_dots:1093174815545888851>")
        ans = SudokuResult(board)
        await asyncio.to_thread(ans.prettify)
        if len(ans.ans) == 1:
            break
    
    userBoards.new_board(interaction.user.id, board, ans.ans[0], difficulty, last_board_img)
    await interaction.edit_original_response(
        content = await userBoards.get_board_msg(interaction.user.id, log_channel),
        view = SudokuView(interaction.user.id, interaction, log_channel)
    )

if __name__ == '__main__':
    bot.run(BOT_TOKEN)