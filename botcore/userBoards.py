import os
import pickle
import discord
from io import BytesIO
import drawer
from drawer import Animation
from botcore import descript
from botcore.classes import BoardData
from localVals import BOARD_DATA_PATH
import asyncio

user_nowid = {}
user_datas = {}
if os.path.isfile(BOARD_DATA_PATH):
    with open(BOARD_DATA_PATH, 'rb') as f:
        user_datas = pickle.load(f)

def have_board(userid: int) -> bool:
    if user_datas.get(str(userid)):
        return True
    return False

def set_user_nowid(userid: int, nowid: int) -> None:
    user_nowid[userid] = nowid
    
def get_user_nowid(userid: int) -> int:
    return user_nowid.get(userid)

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

def new_board(userid: int, board: list[list[int]], ans_board: list[list[int]], difficulty: int, last_image_msgID: int | None) -> None:
    board_data = {
        "board": board,
        "user_ans_board": [[0]*9 for i in range(9)],
        "hint_board": [[0]*9 for i in range(9)],
        "ans_board": ans_board,
        "difficulty": difficulty,
        "last_image_msgID": last_image_msgID,
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
    

async def get_board_msg(userid: int, log_channel: discord.channel, check_done: bool = False) -> str:
    board_data = get_user_board(userid)
    board_img = await asyncio.to_thread(drawer.draw_board, board_data)
    if check_done:
        correct, wrong_board = check_ans(userid)
        ani = Animation(board_img)
        await asyncio.to_thread(ani.animation_scan, wrong_board)
        if correct:
            await asyncio.to_thread(ani.animation_correct)
    else:
        board_img = await asyncio.to_thread(drawer.highlight_board, board_data, board_img)
        
    with BytesIO() as image_binary:
        if check_done:
            ani.frames[0].save(image_binary, format='GIF', save_all=True, append_images=ani.frames[1:], duration=33)
            filename = "board.gif"
        else:
            board_img.save(image_binary, format='PNG')
            filename = "board.png"
        image_binary.seek(0)
        img_msg = await log_channel.send(file=discord.File(fp=image_binary, filename=filename))
        if board_data.last_image_msgID:
            try:
                del_img_msg = await log_channel.fetch_message(board_data.last_image_msgID)
                await del_img_msg.delete()
            except:
                pass
        board_data.last_image_msgID = img_msg.id
        set_user_board(userid, board_data)
        return (
            f"Difficulty: {descript.difficulty_list[board_data.difficulty]}\n"+
            f"Selected cell: {board_data.get_cell_num()}\n"+
            img_msg.attachments[0].url
        )