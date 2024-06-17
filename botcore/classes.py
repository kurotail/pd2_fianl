from discord.ext import commands

class Cog_Extension(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

class BoardData():
    def __init__(self, board_data: dict) -> None:
        self.is_finish = False
        self.last_image_msgID: int = board_data.get("last_image_msgID")
        self.board: list[list[int]] = board_data.get("board")
        self.user_ans_board: list[list[int]] = board_data.get("user_ans_board")
        self.hint_board: list[list[int]] = board_data.get("hint_board")
        self.ans_board: list[list[int]] = board_data.get("ans_board")
        self.difficulty: int = board_data.get("difficulty")
        self.x: int = board_data.get("x")
        self.y: int = board_data.get("y")
    
    def write_number(self, num: int) -> None:
        self.hint_board[self.y][self.x] = 0
        self.user_ans_board[self.y][self.x] = num
    
    def set_hint(self) -> None:
        self.user_ans_board[self.y][self.x] = 0
        self.hint_board[self.y][self.x] = self.ans_board[self.y][self.x]
        
    def set_pos(self, x: int, y: int) -> None:
        if 0 <= x < 9 and 0 <= y < 9:
            self.x = x
            self.y = y
            
    def set_pos_cell_num(self, cell_num: int) -> None:
        if 1 <= cell_num <= 81:
            self.x, self.y = ((cell_num-1) % 9, (cell_num-1) // 9)
    
    def move_up(self) -> None:
        if self.y > 0:
            self.y -= 1
    
    def move_down(self) -> None:
        if self.y < 8:
            self.y += 1
            
    def move_left(self) -> None:
        if self.x > 0:
            self.x -= 1
            
    def move_right(self) -> None:
        if self.x < 8:
            self.x += 1
            
    def reset_board(self) -> None:
        for y in range(9):
            for x in range(9):
                self.user_ans_board[y][x] = 0
                self.hint_board[y][x] = 0
    
    def get_cell_num(self) -> int:
        return self.y*9 + self.x + 1
    
    def set_finish(self, val: bool) -> None:
        self.is_finish = val