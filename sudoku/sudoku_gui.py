import tkinter, keyboard, functools, threading, sudoku
import tkinter.font as tkfont

class win:
    def __init__(self, master: tkinter.Tk) -> None:
        self.color_arr = ["#dddddd", "#ffffff"]
        self.master = master
        self.board_button = []
        self.active = 0
        self.stat = []
        t = threading.Thread(target=self.input_data, daemon=True)
        t.start()

    def build(self):
        board_font = tkfont.Font(self.master, size=18, weight='bold', family='Arial')
        control_font = tkfont.Font(self.master, size=18, family='Arial')
        massage_font = tkfont.Font(self.master, size=14, family='Arial')

        for i in range(9):
            for j in range(9):
                cell_color = self.color_arr[((j // 3) + (i // 3) * 3) % 2]
                self.stat.append(0)
                self.board_button.append(
                    tkinter.Button(
                        self.master,
                        width = 3,
                        height = 1,
                        text = '',
                        justify = 'center',
                        font = board_font,
                        bg = cell_color,
                        activebackground = '#525bde',
                        relief = 'ridge',
                        command = functools.partial(self.activate, i*9+j)
                    )
                )
                self.board_button[i*9+j].place(x = 30+j*55, y = 30+i*50)

        enter_button = tkinter.Button(
            self.master,
            width = 8,
            height = 1,
            text = 'Enter',
            justify = 'center',
            font = control_font,
            bg = '#abbad9',
            activebackground = '#abbad9',
            relief = 'flat',
            command = self.command_enter
        ) 
        enter_button.place(x=536, y=300)

        clear_button = tkinter.Button(
            self.master,
            width=8,
            height=1,
            text='Clear',
            justify='center',
            font=control_font,
            bg='#fc973f',
            activebackground='#fc973f',
            relief='flat',
            command=self.command_clear
        )
        clear_button.place(x=536, y=250)
        
        self.massage = tkinter.Label(self.master, textvariable='', font=massage_font, fg='#3ed64d')
        self.massage.place(x=540, y=170)

    def command_enter(self):
        self.massage.config(text='')
        sample = [[9, 0, 0, 0, 0, 0, 0, 0, 2], [0, 0, 3, 7, 0, 9, 8, 0, 0], [0, 0, 4, 3, 6, 0, 1, 0, 0], [1, 0, 6, 0, 0, 0, 2, 0, 8], [0, 0, 9, 0, 4, 0, 7, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 7, 1, 3, 0, 6, 0, 0], [0, 0, 2, 6, 0, 5, 9, 0, 0], [3, 0, 0, 0, 0, 0, 0, 0, 7]]
        for i in range(81):
            sample[i//9][i%9] = self.stat[i]
        outcome = sudoku.result(sample)
        if outcome.count > 1:
            self.massage.config(text='There are\nmultiple\nanswers!', fg='#ed0c2a')
        elif not outcome.HasSolution:
            self.massage.config(text='There are no\nanswer!', fg='#ed0c2a')
        else:
            j = 0
            for y in range(9):
                for x in range(9):
                    self.stat[j] = outcome.ans[0][y][x]
                    j += 1
            self.display_board()
            self.massage.config(text='Solved.', fg='#3ed64d')

    def command_clear(self):
        self.massage.config(text='')
        for i in range(81):
            self.stat[i] = 0
        self.display_board()

    def display_board(self):
        for i in range(9):
            for j in range(9):
                if self.stat[i*9+j] == 0:
                    self.board_button[i*9+j]['text'] = ''
                else:
                    self.board_button[i*9+j]['text'] = self.stat[i*9+j]
                
                if i*9+j == self.active:
                    self.board_button[i*9+j]['bg'] = '#abbad9'
                else:
                    self.board_button[i*9+j]['bg'] = self.color_arr[((j // 3) + (i // 3) * 3) % 2]

    def activate(self, ind: int):
        self.massage.config(text='')
        self.active = ind
        self.display_board()
        
    def input_data(self):
        while True:
            press = keyboard.read_key()
            if press.isdigit():
                self.stat[self.active] = int(press)
                self.display_board()


if __name__ == '__main__':
    root = tkinter.Tk()
    root.title('Solving Sudoku')
    root.geometry('675x510')
    root.resizable(0, 0)
    a = win(root).build()
    root.mainloop()