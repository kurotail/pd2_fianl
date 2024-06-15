import discord
from botcore import userBoards
from botcore.classes import BoardData
from botcore.botModals import AnswerModal, SelectCellModal
import time

class SudokuView(discord.ui.View):
    def __init__(self, userid: int, original_interaction: discord.Integration, log_channel: discord.channel):
        super().__init__(timeout = 300)
        self.original_interaction: discord.Integration = original_interaction
        self.log_channel: discord.channel = log_channel
        self.userid: int = userid
        self.board_data: BoardData = userBoards.get_user_board(self.userid)
        self.nowid = int(time.time())
        userBoards.set_user_nowid(self.userid, self.nowid)
        self.update_btn_state()
    
    def check_all_fill(self) -> bool:
        board = self.board_data.board
        user_ans_board = self.board_data.user_ans_board
        for y in range(9):
            for x in range(9):
                if board[y][x] + user_ans_board[y][x] == 0:
                    return False
        return True
    
    def update_btn_state(self) -> None:
        btns = {}
        if self.board_data.is_finish:
            for item in self.children:
                if item.label != "Close":
                    item.disabled = True
            return
        else:
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
        
        if self.check_all_fill() == False:
            btns["Finish"].disabled = True
    
    async def check_nowid_expired(self) -> bool:
        if userBoards.get_user_nowid(self.userid) != self.nowid:
            await self.del_self()
            return True
        return False
    
    async def on_timeout(self) -> None:
        await self.del_self()
        
    async def del_self(self) -> None:
        try:
            await self.original_interaction.delete_original_response()
        except:
            pass
        self.stop()
    
    @discord.ui.button(label = "🔼", style = discord.ButtonStyle.primary)
    async def button_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.check_nowid_expired():
            return
        self.board_data.move_up()
        userBoards.set_user_board(self.userid, self.board_data)
        self.update_btn_state()
        await interaction.response.edit_message(
            content = await userBoards.get_board_msg(self.userid, self.log_channel),
            view = self
        )
    
    @discord.ui.button(label = "🔽", style = discord.ButtonStyle.primary)
    async def button_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.check_nowid_expired():
            return
        self.board_data.move_down()
        userBoards.set_user_board(self.userid, self.board_data)
        self.update_btn_state()
        await interaction.response.edit_message(
            content = await userBoards.get_board_msg(self.userid, self.log_channel),
            view = self
        )
    
    @discord.ui.button(label = "◀️", style = discord.ButtonStyle.primary)
    async def button_left(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.check_nowid_expired():
            return
        self.board_data.move_left()
        userBoards.set_user_board(self.userid, self.board_data)
        self.update_btn_state()
        await interaction.response.edit_message(
            content = await userBoards.get_board_msg(self.userid, self.log_channel),
            view = self
        )
    
    @discord.ui.button(label = "▶️", style = discord.ButtonStyle.primary)
    async def button_right(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.check_nowid_expired():
            return
        self.board_data.move_right()
        userBoards.set_user_board(self.userid, self.board_data)
        self.update_btn_state()
        await interaction.response.edit_message(
            content = await userBoards.get_board_msg(self.userid, self.log_channel),
            view = self
        )
    
    @discord.ui.button(label = "Select", style = discord.ButtonStyle.primary)
    async def button_select(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.check_nowid_expired():
            return
        selectModal = SelectCellModal()
        await interaction.response.send_modal(selectModal)
        await selectModal.wait()
        
        if selectModal.cell_num:
            self.board_data.set_pos_cell_num(selectModal.cell_num)
            userBoards.set_user_board(self.userid, self.board_data)
            self.update_btn_state()
            await self.original_interaction.edit_original_response(
                content = await userBoards.get_board_msg(self.userid, self.log_channel),
                view = self
            )
    
    @discord.ui.button(label = "Write", style = discord.ButtonStyle.secondary)
    async def button_write(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.check_nowid_expired():
            return
        ansModal = AnswerModal(f"填寫答案 (Cell: {self.board_data.get_cell_num()})")
        await interaction.response.send_modal(ansModal)
        await ansModal.wait()
        
        if 0 <= ansModal.answer_num <= 9:
            self.board_data.write_number(ansModal.answer_num)
            userBoards.set_user_board(self.userid, self.board_data)
            self.update_btn_state()
            edit_content = await userBoards.get_board_msg(self.userid, self.log_channel)
            await self.original_interaction.edit_original_response(content = edit_content, view = self)

    @discord.ui.button(label = "Hint", style = discord.ButtonStyle.secondary)
    async def button_hint(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.check_nowid_expired():
            return
        self.board_data.set_hint()
        userBoards.set_user_board(self.userid, self.board_data)
        self.update_btn_state()
        await interaction.response.edit_message(
            content = await userBoards.get_board_msg(self.userid, self.log_channel),
            view = self
        )
        
    @discord.ui.button(label = "Reset", style = discord.ButtonStyle.secondary)
    async def button_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.check_nowid_expired():
            return
        self.board_data.reset_board()
        userBoards.set_user_board(self.userid, self.board_data)
        self.update_btn_state()
        await interaction.response.edit_message(
            content = await userBoards.get_board_msg(self.userid, self.log_channel),
            view = self
        )
        
    @discord.ui.button(label = "Finish", style = discord.ButtonStyle.success)
    async def button_finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.check_nowid_expired():
            return
        if userBoards.check_ans(self.userid)[0]:
            self.board_data.set_finish(True)
        userBoards.set_user_board(self.userid, self.board_data)
        self.update_btn_state()
        await interaction.response.edit_message(content = "正在檢查結果<a:loading_dots:1093174815545888851>", view = self)
        edit_content = await userBoards.get_board_msg(self.userid, self.log_channel, True)
        await self.original_interaction.edit_original_response(content = edit_content, view = self)

    @discord.ui.button(label = "Close", style = discord.ButtonStyle.danger)
    async def button_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.check_nowid_expired():
            return
        await self.del_self()

class ConfirmView(discord.ui.View):
    def __init__(self, original_interaction: discord.Integration = None):
        super().__init__(timeout = 10)
        self.value: bool|None = None
        self.original_interaction: discord.Integration = original_interaction
    
    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.original_interaction.edit_original_response(view = self)
        self.stop()
    
    async def on_timeout(self) -> None:
        await self.del_self()
    
    async def del_self(self) -> None:
        try:
            await self.original_interaction.delete_original_response()
        except:
            pass
        self.stop()
        
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
        await self.del_self()