import os
import json
from localVals import BOARD_DATA_PATH

user_datas = {}
if os.path.isfile(BOARD_DATA_PATH):
    with open(BOARD_DATA_PATH, 'r', encoding='utf-8') as f:
        user_datas = json.load(f)

def have_board(userid:int) -> bool:
    if user_datas.get(str(userid)):
        return True
    return False

def set_user_board(userid:int, board_data:dict) -> None:
    user_datas[str(userid)] = board_data
    with open(BOARD_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(user_datas, f, indent=4)

def get_user_board(userid:int) -> dict | None:
    return user_datas.get(str(userid))

def new_board(userid:int, board:list, ans_board:list, difficulty:int) -> None:
    board_data = {
        "board": board,
        "ans_board": ans_board,
        "difficulty": difficulty,
        "x": 0,
        "y": 0
    }
    set_user_board(userid, board_data)

def delete_board(userid:int) -> None:
    user_datas.pop(str(userid), None)
    with open(BOARD_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(user_datas, f, indent=4)