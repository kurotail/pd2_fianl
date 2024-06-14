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

def get_cell_num(x: int, y: int) -> int:
    return y*9 + x + 1

def get_cell_pos(cell_num: int) -> tuple:
    return ((cell_num-1) % 9, (cell_num-1) // 9)

async def get_board_msg(userid: int, log_channel: discord.channel) -> str:
    board_data = get_user_board(userid)
    board_img = await asyncio.to_thread(drawer.draw_board, board_data)
    board_img = await asyncio.to_thread(drawer.highlight_board, board_data, board_img)
    with BytesIO() as image_binary:
        board_img.save(image_binary, 'PNG')
        image_binary.seek(0)
        img_msg = await log_channel.send(file=discord.File(fp=image_binary, filename='board.png'))
        if board_data.last_image_msgID:
            del_img_msg = await log_channel.fetch_message(board_data.last_image_msgID)
            await del_img_msg.delete()
        board_data.last_image_msgID = img_msg.id
        return (
            f"Difficulty: {descrip.difficulty_list[board_data.difficulty]}\n"+
            f"Selected cell: {get_cell_num(board_data.x, board_data.y)}\n"+
            img_msg.attachments[0].url
        )