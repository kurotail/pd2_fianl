import discord
from discord.ext import commands
from botcore import userBoards

class SudokuView(discord.ui.View):
    def __init__(self, ctx: commands.Context, message: discord.message, log_channel: discord.channel):
        super().__init__(timeout = 60)
        self.message: discord.message = message
        self.log_channel: discord.channel = log_channel
        self.ctx: commands.Context = ctx
        self.player_id: int = ctx.author.id
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
        await self.message.delete()

    @discord.ui.button(label = "🔼", style = discord.ButtonStyle.primary)
    async def button_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board_data['y'] -= 1
        userBoards.set_user_board(self.player_id, self.board_data)
        self.btn_boundary_state()
        await interaction.response.edit_message(
            content = await userBoards.get_board_msg(self.ctx.author.id, self.log_channel),
            view = self
        )
    
    @discord.ui.button(label = "🔽", style = discord.ButtonStyle.primary)
    async def button_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board_data['y'] += 1
        userBoards.set_user_board(self.player_id, self.board_data)
        self.btn_boundary_state()
        await interaction.response.edit_message(
            content = await userBoards.get_board_msg(self.ctx.author.id, self.log_channel),
            view = self
        )
    
    @discord.ui.button(label = "◀️", style = discord.ButtonStyle.primary)
    async def button_left(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board_data['x'] -= 1
        userBoards.set_user_board(self.player_id, self.board_data)
        self.btn_boundary_state()
        await interaction.response.edit_message(
            content = await userBoards.get_board_msg(self.ctx.author.id, self.log_channel),
            view = self
        )
    
    @discord.ui.button(label = "▶️", style = discord.ButtonStyle.primary)
    async def button_right(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board_data['x'] += 1
        userBoards.set_user_board(self.player_id, self.board_data)
        self.btn_boundary_state()
        await interaction.response.edit_message(
            content = await userBoards.get_board_msg(self.ctx.author.id, self.log_channel),
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
        try:
            await self.message.edit(view = self)
            self.stop()
        except:
            pass
    
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