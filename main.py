#discord bot "sudokun"

import discord
import discord.context_managers
from discord.ext import commands
from discord import app_commands
from sudoku.sudoku import SudokuResult
from crawler import SudokuCrawler
from botcore import descrip, userBoards
from botcore.botViews import SudokuView, ConfirmView
from localVals import *
import asyncio

class Bot(commands.Bot):

    def __init__(self) -> None:
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="w!",
            intents=intents,
            help_command=None,
            activity=discord.Game(name="指令前綴：w!")
        )

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=discord.Object(id = GUILD_ID))
        print(f"Now login user: {self.user}.")

    async def on_command_error(self, ctx, error) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            delmsg = await ctx.reply(
                f"Cooldown（冷卻中）：{round(error.retry_after, 2)}s",
                ephemeral=True)
        elif isinstance(error, commands.CommandNotFound):
            delmsg = await ctx.reply('Command Not Found（查無此指令）！',
                                     ephemeral=True)
        else:
            delmsg = await ctx.reply(error, ephemeral=True)
            
        await asyncio.sleep(3)
        
        try:
            await ctx.message.delete()
            await delmsg.delete()
        except:
            pass


bot = Bot()
sudoku_crawler = SudokuCrawler()

@bot.hybrid_command(name="start_sudoku", with_app_command=True, description=descrip.start_sudoku)
@commands.cooldown(1, 10, commands.BucketType.user)
@app_commands.guilds(discord.Object(id = GUILD_ID))
async def start_sudoku(ctx: commands.Context) -> None:
    await ctx.defer(ephemeral = True)
    reply_msg = await ctx.reply("正在讀取資料 <a:loading_dots:1093174815545888851>")
    log_channel = bot.get_channel(1250654346861875200)
    
    if userBoards.have_board(ctx.author.id) == False:
        await reply_msg.edit(content = "您沒有遊戲紀錄，請使用 /new_sudoku 來開啟新遊戲")
        return
    
    await reply_msg.edit(
        content = await userBoards.get_board_msg(ctx.author.id, log_channel),
        view = SudokuView(ctx, reply_msg, log_channel)
    )

@bot.hybrid_command(name="new_sudoku", with_app_command=True, description=descrip.new_sudoku)
@commands.cooldown(1, 10, commands.BucketType.user)
@app_commands.describe(difficulty = descrip.new_sudoku_difficulty)
@app_commands.guilds(discord.Object(id = GUILD_ID))
async def new_sudoku(ctx: commands.Context, difficulty:int) -> None:
    await ctx.defer(ephemeral = True)
    reply_msg = await ctx.reply("正在爬取題目 <a:loading_dots:1093174815545888851>")
    log_channel = bot.get_channel(1250654346861875200)
    
    if userBoards.have_board(ctx.author.id):
        
        confirm_view = ConfirmView(reply_msg)
        await reply_msg.edit(
            content = "您已經有一場遊戲紀錄了，您是否要開始新的遊戲？",
            view = confirm_view
        )
        await confirm_view.wait() #等待回復是否開啟新遊戲
        
        if confirm_view.value == False: #不開啟新遊戲
            
            confirm_view = ConfirmView(reply_msg)
            await reply_msg.edit(
                content = "是否繼續上次的遊戲？",
                view = confirm_view   
            )
            await confirm_view.wait() #等待回復是否繼續上次遊戲
            
            if confirm_view.value: #繼續上次遊戲
                await reply_msg.edit(
                    content = await userBoards.get_board_msg(ctx.author.id, log_channel),
                    view = SudokuView(ctx, reply_msg, log_channel)
                )
                return
            
        if confirm_view.value != True: #按下取消或不繼續上次遊戲
            return
    
    while True:
        await reply_msg.edit(content = "正在爬取題目 <a:loading_dots:1093174815545888851>")
        try:
            board = await sudoku_crawler.crawlBoard(difficulty)
        except ValueError:
            await reply_msg.edit(content = "難度必須在 0~3 之間")
            return
        
        await reply_msg.edit(content = "正在分析題目 <a:loading_dots:1093174815545888851>")
        ans = SudokuResult(board)
        await asyncio.to_thread(ans.prettify)
        if len(ans.ans) == 1:
            break
        
    userBoards.new_board(ctx.author.id, board, ans.ans, difficulty)
    await reply_msg.edit(
        content = await userBoards.get_board_msg(ctx.author.id, log_channel),
        view = SudokuView(ctx, reply_msg, log_channel)
    )

if __name__ == '__main__':
    bot.run(BOT_TOKEN)