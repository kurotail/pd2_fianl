import os
import pickle

user_datas = {}
if os.path.isfile("./board_data.pickle"):
    with open("./board_data.pickle", 'rb') as f:
        user_datas = pickle.load(f)
        