#090623
class _board:
    def __init__(self, raw):
        temp1 = []
        temp2 = []
        for a in raw:
            for b in list(a):
                if int(b) == 0:
                    temp2.append([1,2,3,4,5,6,7,8,9])
                if int(b) != 0:
                    temp2.append(int(b))
            temp1.append(temp2)
            temp2 = []
        self.stat = temp1
        self.dreport = False
        self.oreport = False

    def colum(self, x):
        temp = []
        for i in range(9):
            temp.append(self.stat[i][x])
        return(temp)

    def row(self, y):
        return(self.stat[y])

    def block(self, x, y):
        temp1 = []
        temp2 = []
        bx = 0
        by = 0

        temp1 = [x//3, y//3]
        bx = temp1[0] * 3
        by = temp1[1] * 3
        temp2 = self.stat[by][bx : bx + 3] + self.stat[by + 1][bx : bx + 3] + self.stat[by + 2][bx : bx + 3]

        return(temp2)

    def delet(self, x, y):
        temp1 = self.stat
        if type(self.stat[y][x]) == list:
            for r in self.row(y):
                if type(r) == int:
                    if self.stat[y][x].count(r) == 1:
                        temp1[y][x].remove(r)
                        self.dreport = True
            
            for c in self.colum(x):
                if type(c) == int:
                    if self.stat[y][x].count(c) == 1:
                        temp1[y][x].remove(c)
                        self.dreport = True

            for b in self.block(x, y):
                if type(b) == int:
                    if self.stat[y][x].count(b) == 1:
                        temp1[y][x].remove(b)
                        self.dreport = True
                
            if len(self.stat[y][x]) == 1:
                temp1[y][x] = self.stat[y][x][0]
                self.dreport = True

        self.stat = temp1

    def dloop(self):
        self.dreport = True
        while self.dreport:
            self.dreport = False
            for x in range(9):
                for y in range(9):
                    self.delet(x, y)

    def only(self, t):
        pos = [[0, 0], [3, 0], [6, 0], [0, 3], [3, 3], [6, 3], [0, 6], [3, 6], [6, 6]]
        
        num2ind = [[], [], [], [], [], [], [], [], [], []]
        self.dloop()
        for i in range(9):
            if type(self.row(t)[i]) == list:
                for p in self.row(t)[i]:
                    num2ind[p].append({'x':i, 'y':t})
        for num in range(1,10):
            if len(num2ind[num]) == 1:
                self.stat[num2ind[num][0]['y']][num2ind[num][0]['x']] = num
                self.oreport = True

        num2ind = [[], [], [], [], [], [], [], [], [], []]
        self.dloop()
        for i in range(9):
            if type(self.colum(t)[i]) == list:
                for p in self.colum(t)[i]:
                    num2ind[p].append({'x':t, 'y':i})
        for num in range(1,10):
            if len(num2ind[num]) == 1:
                self.stat[num2ind[num][0]['y']][num2ind[num][0]['x']] = num
                self.oreport = True

        num2ind = [[], [], [], [], [], [], [], [], [], []]
        self.dloop()
        for i in range(9):
            if type(self.block(pos[t][0], pos[t][1])[i]) == list:
                for p in self.block(pos[t][0], pos[t][1])[i]:
                    num2ind[p].append({'x':pos[t][0] + (i % 3), 'y':pos[t][1] + (i // 3)})
        for num in range(1, 10):
            if len(num2ind[num]) == 1:
                self.stat[num2ind[num][0]['y']][num2ind[num][0]['x']] = num
                self.oreport = True

    def simplify(self):
        self.oreport = True
        while self.oreport:
            self.dloop()
            self.oreport = False
            for t in range(9):
                self.only(t)

    def recons(self):
        temp1 = [[[xx, yy] for xx in range(9)] for yy in range(9)]
        for y in range(9):
            for x in range(9):
                if type(self.stat[y][x]) == list:
                    temp1[y][x] = 0
                else:
                    temp1[y][x] = self.stat[y][x]
        return(temp1)

class _pri:
    def __init__(self, raw):
        self.InputCheck(raw)
        self.futures = [_board(raw)]
        self.nows = []
        self.futures[0].simplify()
        self.ans = []
        self.futures_solve()

    def futures_solve(self) -> None:
        done_ = False
        self.nows = []
        temp1 = [ii for ii in range(len(self.futures))]
        err = False
        for i in range(len(self.futures)):
            for y in range(9):
                for x in range(9):
                    if type(self.futures[i].stat[y][x]) == list and len(self.futures[i].stat[y][x]) == 0:
                        temp1.remove(i)
                        err = True
                        break
                if err:
                    break
            err = False
        for ind in temp1:
            done_ = True
            for y in self.futures[ind].stat:
                for x in y:
                    if type(x) == list:
                        done_ = False
            if done_:
                self.ans.append(self.futures[ind].stat)
            else:
                self.nows.append(self.futures[ind])

    def expend(self) -> None:
        temp1 = []
        hasfound = False
        self.futures = []
        for i in self.nows:
            for y in range(9):
                for x in range(9):
                    if type(i.stat[y][x]) == list:
                        hasfound = True
                        pos = [y, x]
                        break
                if hasfound:
                    break
            hasfound = False
            for n in i.stat[pos[0]][pos[1]]:
                temp1 = i.recons()
                temp1[pos[0]][pos[1]] = n
                temp2 = _board(temp1)
                temp2.simplify()
                self.futures.append(temp2)

    def InputCheck(self, board: list) -> None:
        if type(board) != list:
            raise TypeError('A board shoud be a two-dimensional list.')
        elif len(board) != 9:
            raise ValueError('A board should contain 81 integers, in the form of a two-dimensional list.')
        for outer in board:
            if type(outer) != list:
                raise TypeError('A board shoud be a two-dimensional list.')
            elif len(outer) != 9:
                raise ValueError('A board should contain 81 integers, in the form of a two-dimensional list.')
            for inner in outer:
                if type(inner) != int:
                    raise TypeError('A board should contain 81 integers, in the form of a two-dimensional list.')
                elif inner < 0 or inner > 9:
                    raise ValueError('The integers in a board should be between 0 to 9.  "0" means the number remaining unknown.')

class result:
    ans: list
    HasSolution: bool
    count: int

    def __init__(self, board) -> None:
        '''
        Arg "board" accept both str and list of int.

        For str, 
        A board shoud be a str seperate 9 sub str by comma.
        A board should contain 81 integers, 9 in each sub str.

        For list, 
        A board shoud be a two-dimensional list.
        A board should contain 81 integers, in the form of a two-dimensional list.

        Both of them the integers in a board should be between 0 to 9.  "0" means the number remaining unknown.
        '''
        self.board = board
        self.solve()
    
    def prettify(self, print_out: bool = False) -> str:
        for qwert in self.ans:
            answers = '========================\n'
            for asdfg in qwert:
                answers = answers + str(asdfg) + '\n'
            answers = answers + '========================'
        if print_out:
            print(answers)
        return(answers)

    def solve(self):
        if type(self.board) == str:
            board = self.transform(self.board)
        else:
            board = self.board
        a = _pri(board)

        while len(a.nows):
            a.expend()
            a.futures_solve()
        self.ans = a.ans
        self.HasSolution = bool(len(a.ans))
        self.count = len(a.ans)
    
    def transform(self, board: str) -> list:
        if type(board) != str:
            raise TypeError('Input should be a string.')
        question = []
        for x in board.split(','):
            question.append([int(b) for b in list(x)])
        return(question)
    

#testing
if __name__ == "__main__":
    ans = result([[9, 0, 0, 0, 0, 0, 0, 0, 2], [0, 0, 3, 7, 0, 9, 8, 0, 0], [0, 0, 4, 3, 6, 0, 1, 0, 0], [1, 0, 6, 0, 0, 0, 2, 0, 8], [0, 0, 9, 0, 4, 0, 7, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 7, 1, 3, 0, 6, 0, 0], [0, 0, 2, 6, 0, 5, 9, 0, 0], [3, 0, 0, 0, 0, 0, 0, 0, 7]])
    ans.prettify(True)
    print(ans.ans)

#'900000002,003709800,004360100,106000208,009040700,000000000,007130600,002605900,300000007'
#[[9, 0, 0, 0, 0, 0, 0, 0, 2], [0, 0, 3, 7, 0, 9, 8, 0, 0], [0, 0, 4, 3, 6, 0, 1, 0, 0], [1, 0, 6, 0, 0, 0, 2, 0, 8], [0, 0, 9, 0, 4, 0, 7, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 7, 1, 3, 0, 6, 0, 0], [0, 0, 2, 6, 0, 5, 9, 0, 0], [3, 0, 0, 0, 0, 0, 0, 0, 7]]
