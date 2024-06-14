import os
import pickle
import discord
from io import BytesIO
import drawer
from botcore import descrip
from botcore.classes import BoardData
from localVals import BOARD_DATA_PATH
import asyncio

user_datas = {}
if os.path.isfile(BOARD_DATA_PATH):
    with open(BOARD_DATA_PATH, 'rb') as f:
        user_datas = pickle.load(f)

def have_board(userid: int) -> bool:
    if user_datas.get(str(userid)):
        return True
    return False

def set_user_board(userid: int, board_data: BoardData) -> None:
    user_datas[str(userid)] = board_data
    with open(BOARD_DATA_PATH, 'wb') as f:
        pickle.dump(user_datas, f)

def get_user_board(userid:int) -> BoardData | None:
    return user_datas.get(str(userid))

def delete_board(userid: int) -> None:
    user_datas.pop(str(userid), None)
    with open(BOARD_DATA_PATH, 'wb') as f:
        pickle.dump(user_datas, f)
        
def new_board(userid: int, board: list[list[int]], ans_board: list[list[int]], difficulty: int) -> None:
    board_data = {
        "board": board,
        "user_ans_board": [[0]*9 for i in range(9)],
        "hint_board": [[0]*9 for i in range(9)],
        "ans_board": ans_board,
        "difficulty": difficulty,
        "x": 0,
        "y": 0
    }
    set_user_board(userid, BoardData(board_data))

def check_ans(userid: int) -> tuple[bool, list[list[bool]]]:
    """
    Return a tuple(bool, list[list[int]])
    [0]: whether the answer is correct.
    [1]: 2D-list marking the positions with incorrect answers as True.
    """
    board_data = get_user_board(userid)
    ans_correct = True
    wrong_board = [[False]*9 for i in range(9)]
    user_ans_board = board_data.user_ans_board
    ans_board = board_data.ans_board
    board = board_data.board
    for y in range(9):
        for x in range(9):
            if user_ans_board[y][x] != ans_board[y][x] and board[y][x] == 0:
                wrong_board[y][x] = True
                ans_correct = False
    
    return (ans_correct, wrong_board)
    

async def get_board_msg(userid: int, log_channel: discord.channel) -> str:
    board_data = get_user_board(userid)
    board_img = await asyncio.to_thread(drawer.draw_board, board_data)
    board_img = await asyncio.to_thread(drawer.highlight_board, board_data, board_img)
    with BytesIO() as image_binary:
        board_img.save(image_binary, 'PNG')
        image_binary.seek(0)
        img_msg = await log_channel.send(file=discord.File(fp=image_binary, filename='board.png'))
        if board_data.last_image_msgID:
            try:
                del_img_msg = await log_channel.fetch_message(board_data.last_image_msgID)
                await del_img_msg.delete()
            except:
                pass
        board_data.last_image_msgID = img_msg.id
        return (
            f"Difficulty: {descrip.difficulty_list[board_data.difficulty]}\n"+
            f"Selected cell: {board_data.get_cell_num()}\n"+
            img_msg.attachments[0].url
        )