#discord bot "sudokun"

import discord
import discord.context_managers
from discord.ext import commands
from discord import app_commands
from sudoku.sudoku import SudokuResult
from sudoku import drawer
from crawler import SudokuCrawler
from botcore import descrip, userBoards
from localVals import *
from PIL import Image
from io import BytesIO
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

class SudokuView(discord.ui.View):
    def __init__(self, ctx:commands.Context, message:discord.message):
        super().__init__(timeout = 60)
        self.message: discord.message = message
        self.player_id: int = ctx.author.id
        self.ctx: commands.Context = ctx
        self.board_data: dict = userBoards.get_user_board(self.player_id)
        self.btn_boundary_state()
        
    def btn_boundary_state(self) -> None:
        btns = {"🔼":None, "🔽":None, "◀️":None, "▶️":None}
        for item in self.children:
            if item.label in btns.keys():
                btns[item.label] = item
                item.disabled = False
        
        if self.board_data['y'] == 0:
            btns["🔼"].disabled = True
        elif self.board_data['y'] == 8:
            btns["🔽"].disabled = True
        if self.board_data['x'] == 0:
            btns["◀️"].disabled = True
        elif self.board_data['x'] == 8:
            btns["▶️"].disabled = True
        
    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)
        self.stop()
    
    async def on_timeout(self) -> None:
        await self.disable_all_items()

    @discord.ui.button(label = "🔼", style = discord.ButtonStyle.primary)
    async def button_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board_data['y'] -= 1
        userBoards.set_user_board(self.player_id, self.board_data)
        self.btn_boundary_state()
        await interaction.response.edit_message(
            content = await get_board_msg(self.ctx.author.id),
            view = self
        )
    
    @discord.ui.button(label = "🔽", style = discord.ButtonStyle.primary)
    async def button_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board_data['y'] += 1
        userBoards.set_user_board(self.player_id, self.board_data)
        self.btn_boundary_state()
        await interaction.response.edit_message(
            content = await get_board_msg(self.ctx.author.id),
            view = self
        )
    
    @discord.ui.button(label = "◀️", style = discord.ButtonStyle.primary)
    async def button_left(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board_data['x'] -= 1
        userBoards.set_user_board(self.player_id, self.board_data)
        self.btn_boundary_state()
        await interaction.response.edit_message(
            content = await get_board_msg(self.ctx.author.id),
            view = self
        )
    
    @discord.ui.button(label = "▶️", style = discord.ButtonStyle.primary)
    async def button_right(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board_data['x'] += 1
        userBoards.set_user_board(self.player_id, self.board_data)
        self.btn_boundary_state()
        await interaction.response.edit_message(
            content = await get_board_msg(self.ctx.author.id),
            view = self
        )

class ConfirmView(discord.ui.View):
    def __init__(self, message: discord.message = None):
        super().__init__(timeout = 10)
        self.value: bool|None = None
        self.message: discord.message = message
    
    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view = self)
        self.stop()
    
    async def on_timeout(self) -> None:
        await self.disable_all_items()
        
    @discord.ui.button(label = "Yes", style = discord.ButtonStyle.success)
    async def button_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view = self)
        self.value = True
        await self.disable_all_items()
        
    @discord.ui.button(label = "No", style = discord.ButtonStyle.danger)
    async def button_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view = self)
        self.value = False
        await self.disable_all_items()
    
    @discord.ui.button(label = "Cancel", style = discord.ButtonStyle.secondary)
    async def button_cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view = self)
        self.value = None
        await self.disable_all_items()

bot = Bot()
sudoku_crawler = SudokuCrawler()

async def get_board_msg(userid:int) -> str:
    board_data = userBoards.get_user_board(userid)
    board_img = drawer.draw_board(board_data['board'])
    board_img = drawer.highlight_board(board_data['board'], board_data['x'], board_data['y'], board_img)
    with BytesIO() as image_binary:
        board_img.save(image_binary, 'PNG')
        image_binary.seek(0)
        log_channel = bot.get_channel(1250654346861875200)
        img_msg = await log_channel.send(file=discord.File(fp=image_binary, filename='board.png'))
        return (
            f"Difficulty: {descrip.difficulty_list[board_data['difficulty']]}\n"+
            "Selected cell: 1\n"+
            img_msg.attachments[0].url
        )
    
    
@bot.hybrid_command(name="start_sudoku", with_app_command=True, description=descrip.start_sudoku)
@commands.cooldown(1, 10, commands.BucketType.user)
@app_commands.describe(difficulty = descrip.start_sudoku_difficulty)
@app_commands.guilds(discord.Object(id = GUILD_ID))
async def start_sudoku(ctx: commands.Context, difficulty:int) -> None:
    await ctx.defer(ephemeral = True)
    reply_msg = await ctx.reply("正在爬取題目 <a:loading_dots:1093174815545888851>")
    
    if userBoards.have_board(ctx.author.id):
        
        confirm_view = ConfirmView(reply_msg)
        await reply_msg.edit(
            content = "您已經有一場遊戲紀錄了，您是否要開始新的遊戲？",
            view = confirm_view
        )
        await confirm_view.wait() #等待回復是否開啟新遊戲
        
        if confirm_view.value: #開啟新遊戲
            await reply_msg.edit(content = "正在爬取題目 <a:loading_dots:1093174815545888851>")
        elif confirm_view.value == False: #不開啟新遊戲
            
            confirm_view = ConfirmView(reply_msg)
            await reply_msg.edit(
                content = "是否繼續上次的遊戲？",
                view = confirm_view   
            )
            await confirm_view.wait() #等待回復是否繼續上次遊戲
            
            if confirm_view.value: #繼續上次遊戲
                await reply_msg.edit(
                    content = await get_board_msg(ctx.author.id),
                    view = SudokuView(ctx, reply_msg)
                )
                return
            
        if confirm_view.value != True: #按下取消或不繼續上次遊戲
            await reply_msg.delete()
            return
    
    try:
        board = await sudoku_crawler.crawlBoard(difficulty)
    except ValueError:
        await reply_msg.edit(content = "難度必須在 0~3 之間")
        return
    
    await reply_msg.edit(content = "正在分析題目 <a:loading_dots:1093174815545888851>")
    ans = SudokuResult(board)
    await asyncio.to_thread(ans.prettify)
    userBoards.new_board(ctx.author.id, board, ans.ans, difficulty)
    
    await reply_msg.edit(
        content = await get_board_msg(ctx.author.id),
        view = SudokuView(ctx, reply_msg)
    )

if __name__ == '__main__':
    bot.run(BOT_TOKEN)