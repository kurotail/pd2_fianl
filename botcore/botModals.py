import discord

class AnswerModal(discord.ui.Modal):
    def __init__(self, title: str) -> None:
        super().__init__(title = title)
        self.add_item(discord.ui.TextInput(
            style = discord.TextStyle.short,
            label = "Answer",
            required = False,
            placeholder = "0~9 or blank"
        ))
        self.answer_num: int = 0
        self.status: str = ""
        
    async def on_submit(self, interaction: discord.Interaction) -> None:
        num = 0
        if self.children[0].value != "":
            try:
                num = int(self.children[0].value)
                if num < 0 or num > 9:
                    self.status = "輸入錯誤，請輸入 0~9 or blank"
            except:
                self.status = "輸入錯誤，請輸入 0~9 or blank"
        
        if self.status != "":
            await interaction.response.send_message(self.status, ephemeral=True)
        else:
            self.answer_num = num
            await interaction.response.defer(ephemeral=True)
        self.stop()
        
class SelectCellModal(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title = "選擇表格")
        self.add_item(discord.ui.TextInput(
            style = discord.TextStyle.short,
            label = "Cell Index",
            required = False,
            placeholder = "數字 (1~81 由左至右，由上而下)"
        ))
        self.cell_num: int = 0
        self.status: str = ""
        
    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            num = int(self.children[0].value)
            if num < 1 or num > 81:
                self.status = "請輸入整數 (1~81)"
        except:
            self.status = "請輸入整數 (1~81)"
        
        if self.status != "":
            await interaction.response.defer(ephemeral=True)
        else:
            self.cell_num = num
            await interaction.response.defer(ephemeral=True)
        self.stop()