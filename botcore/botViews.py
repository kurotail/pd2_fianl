import discord
from discord.ext import commands
from botcore import userBoards
from botcore.classes import BoardData
from botcore.botModals import AnswerModal, SelectCellModal

class SudokuView(discord.ui.View):
    def __init__(self, ctx: commands.Context, message: discord.message, log_channel: discord.channel):
        super().__init__(timeout = 300)
        self.message: discord.message = message
        self.log_channel: discord.channel = log_channel
        self.ctx: commands.Context = ctx
        self.player_id: int = ctx.author.id
        self.board_data: BoardData = userBoards.get_user_board(self.player_id)
        self.btn_boundary_state()
        
    def btn_boundary_state(self) -> None:
        btns = {}
        for item in self.children:
            btns[item.label] = item
            item.disabled = False

        if self.board_data.y == 0:
            btns['🔼'].disabled = True
        elif self.board_data.y == 8:
            btns['🔽'].disabled = True
        if self.board_data.x == 0:
            btns['◀️'].disabled = True
        elif self.board_data.x == 8:
            btns['▶️'].disabled = True
        
        x = self.board_data.x
        y = self.board_data.y
        if self.board_data.board[y][x]:
            btns["Write"].disabled = True
            btns["Hint"].disabled = True
        
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
        self.board_data.y -= 1
        userBoards.set_user_board(self.player_id, self.board_data)
        self.btn_boundary_state()
        await interaction.response.edit_message(
            content = await userBoards.get_board_msg(self.player_id, self.log_channel),
            view = self
        )
    
    @discord.ui.button(label = "🔽", style = discord.ButtonStyle.primary)
    async def button_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board_data.y += 1
        userBoards.set_user_board(self.player_id, self.board_data)
        self.btn_boundary_state()
        await interaction.response.edit_message(
            content = await userBoards.get_board_msg(self.player_id, self.log_channel),
            view = self
        )
    
    @discord.ui.button(label = "◀️", style = discord.ButtonStyle.primary)
    async def button_left(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board_data.x -= 1
        userBoards.set_user_board(self.player_id, self.board_data)
        self.btn_boundary_state()
        await interaction.response.edit_message(
            content = await userBoards.get_board_msg(self.player_id, self.log_channel),
            view = self
        )
    
    @discord.ui.button(label = "▶️", style = discord.ButtonStyle.primary)
    async def button_right(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.board_data.x += 1
        userBoards.set_user_board(self.player_id, self.board_data)
        self.btn_boundary_state()
        await interaction.response.edit_message(
            content = await userBoards.get_board_msg(self.player_id, self.log_channel),
            view = self
        )
    
    @discord.ui.button(label = "Select", style = discord.ButtonStyle.primary)
    async def button_select(self, interaction: discord.Interaction, button: discord.ui.Button):
        x = self.board_data.x
        y = self.board_data.y
        selectModal = SelectCellModal()
        await interaction.response.send_modal(selectModal)
        await selectModal.wait()
        
        if selectModal.cell_num:
            x, y = userBoards.get_cell_pos(selectModal.cell_num)
            self.board_data.x = x
            self.board_data.y = y
            userBoards.set_user_board(self.player_id, self.board_data)
            self.btn_boundary_state()
            await self.message.edit(
                content = await userBoards.get_board_msg(self.player_id, self.log_channel),
                view = self
            )
    
    @discord.ui.button(label = "Write", style = discord.ButtonStyle.secondary)
    async def button_write(self, interaction: discord.Interaction, button: discord.ui.Button):
        x = self.board_data.x
        y = self.board_data.y
        ansModal = AnswerModal(f"填寫答案 (Cell: {userBoards.get_cell_num(x, y)})")
        await interaction.response.send_modal(ansModal)
        await ansModal.wait()
        
        if ansModal.answer_num:
            self.board_data.hint_board[y][x] = 0
            self.board_data.user_ans_board[y][x] = ansModal.answer_num
            userBoards.set_user_board(self.player_id, self.board_data)
            edit_content = await userBoards.get_board_msg(self.player_id, self.log_channel)
            await self.message.edit(content = edit_content)

    @discord.ui.button(label = "Hint", style = discord.ButtonStyle.secondary)
    async def button_hint(self, interaction: discord.Interaction, button: discord.ui.Button):
        x = self.board_data.x
        y = self.board_data.y
        self.board_data.user_ans_board[y][x] = 0
        self.board_data.hint_board[y][x] = self.board_data.ans_board[0][y][x]
        userBoards.set_user_board(self.player_id, self.board_data)
        self.btn_boundary_state()
        await interaction.response.edit_message(
            content = await userBoards.get_board_msg(self.player_id, self.log_channel),
            view = self
        )

    @discord.ui.button(label = "Close", style = discord.ButtonStyle.danger)
    async def button_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.disable_all_items()
        await self.message.delete()
        self.stop()

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
        await self.message.delete()
        
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
        await self.disable_all_items()
        await self.message.delete()
        self.stop()