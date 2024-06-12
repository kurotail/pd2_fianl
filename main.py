#discord bot "sudokun"

import discord
from localVals import *
from discord.ext import commands
from discord import app_commands
from sudoku.sudoku import SudokuResult
from crawler import SudokuCrawler
from botcore import descrip
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
@commands.cooldown(1, 5, commands.BucketType.user)
@app_commands.describe(difficulty = descrip.start_sudoku_difficulty)
@app_commands.guilds(discord.Object(id = GUILD_ID))
async def start_sudoku(ctx: commands.Context, difficulty:int) -> None:
    await ctx.defer(ephemeral = True)
    process_msg = await ctx.reply("正在爬取題目 <a:loading_dots:1093174815545888851>")
    try:
        board = await sudoku_crawler.crawlBoard(difficulty)
    except ValueError:
        await process_msg.edit(content = "難度必須在 0~3 之間")
        return
    await process_msg.edit(content = "正在分析題目 <a:loading_dots:1093174815545888851>")
    ans = SudokuResult(board)
    await asyncio.to_thread(ans.prettify)
    await process_msg.edit(content = ans.ans)

if __name__ == '__main__':
    bot.run(BOT_TOKEN)