from PIL import Image, ImageDraw, ImageFont
from botcore.classes import BoardData
import localVals

BG_COLOR = "#232428"
GRIDBG_COLOR = ["#383A40", "#2E3035"]
LINE_COLOR = "#F3F4F8"
DEFAULT_NUM_COLOR = "#F3F4F8"
USER_ANS_COLOR = "#2CA4F7"
HINT_COLOR = "#6CD85B"
HIGHLIGHT_COLOR = [
    (255, 255, 255, 50), #box, row, col highlight color
    (175, 211, 243, 100), #selected cell highlight color
    (213, 243, 175, 100) #same number cell highlight color
]

IMGSIZE = (500, 500)
MARGIN = 10
CORRECT_ANI_SIZE = (370, 370)
CORRECT_ANI_OFFSET = (170, 170)
CORRECT_ANI_OFFSET_INIT = (170, 530)

GRID_SIZE = IMGSIZE[0] - 2 * MARGIN
CELL_SIZE = GRID_SIZE // 9

def draw_board(board_data: BoardData) -> Image:
    board = board_data.board
    user_ans_board = board_data.user_ans_board
    hint_board = board_data.hint_board
    image = Image.new("RGBA", IMGSIZE, color=BG_COLOR)
    draw = ImageDraw.Draw(image)

    start_x = MARGIN
    start_y = MARGIN
    for i in range(3):
        for j in range(3):
            draw.rectangle(
                [
                    start_x + j * 3 * CELL_SIZE,
                    start_y + i * 3 * CELL_SIZE,
                    start_x + (j + 1) * 3 * CELL_SIZE,
                    start_y + (i + 1) * 3 * CELL_SIZE
                ],
                fill=GRIDBG_COLOR[(i*3+j) % 2]
            )

    for i in range(10):
        line_width = 1
        if i % 3 == 0:
            line_width = 3
        draw.line( #水平線
            [
                (start_x, start_y + i * CELL_SIZE),
                (start_x + GRID_SIZE-2, start_y + i * CELL_SIZE)
            ],
            fill=LINE_COLOR,
            width=line_width
        )
        draw.line( #垂直線
            [
                (start_x + i * CELL_SIZE, start_y),
                (start_x + i * CELL_SIZE, start_y + GRID_SIZE-2)
            ],
            fill=LINE_COLOR,
            width=line_width
        )

    font = ImageFont.truetype("arial.ttf", 30)
    for row in range(9):
        for col in range(9):
            if board[row][col] or user_ans_board[row][col] or hint_board[row][col]:
                number = str(board[row][col] + user_ans_board[row][col] + hint_board[row][col])
                bbox = font.getbbox(number)
                text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                text_x = start_x + col * CELL_SIZE + (CELL_SIZE - text_width) // 2
                text_y = start_y + row * CELL_SIZE + (CELL_SIZE - text_height) // 2
            if board[row][col]:
                draw.text((text_x+1, text_y-3), number, fill=DEFAULT_NUM_COLOR, font=font)
            if user_ans_board[row][col]:
                draw.text((text_x+1, text_y-3), number, fill=USER_ANS_COLOR, font=font)
            if hint_board[row][col]:
                draw.text((text_x+1, text_y-3), number, fill=HINT_COLOR, font=font)

    return image

def drawCorrectAni(main_image: Image.Image) -> list[Image.Image]:
    """
    Draw a animation with a sign on the right-bottom corner based on main_image.
    Return a list of ```Image``` illustrating the scene of finished a game base on the image of the end.
    Note that it is designed basing on 30fps.
    :param main_image: the animation is based on main_image, which should be a solved game board.
    """
    
    # Create a transparent layer with the same size as the main image
    main_image = main_image.convert("RGBA")
    background = Image.new('RGBA', main_image.size, (0, 0, 0, 0))
    # Load and resize the images
    resized_images: list[Image.Image] = []
    gif = Image.open(localVals.CORRECT_ANI_PATH)
    offset_0 = CORRECT_ANI_OFFSET_INIT[0]
    offset_1 = CORRECT_ANI_OFFSET_INIT[1]
    try:
        while True:
            offset = (offset_0, offset_1)
            gif.seek(gif.tell() + 1)
            frame = gif.copy()
            resized_image: Image.Image = background.copy()
            resized_image.paste(frame.resize(CORRECT_ANI_SIZE), offset)
            resized_images.append(resized_image)
            if abs(offset_0 - CORRECT_ANI_OFFSET[0]) > 10:
                offset_0 += int((CORRECT_ANI_OFFSET[0] - CORRECT_ANI_OFFSET_INIT[0]) / 5)
            if abs(offset_1 - CORRECT_ANI_OFFSET[1]) > 10:
                offset_1 += int((CORRECT_ANI_OFFSET[1] - CORRECT_ANI_OFFSET_INIT[1]) / 5)
    except EOFError:
        pass


    # Create a list to hold the modified images
    modified_images = []
    
    for img in resized_images:
        modified_images.append(Image.alpha_composite(main_image, img))
    
    return modified_images

def highlight_board(board_data: BoardData, image:Image) -> Image:
    board = board_data.board
    user_ans_board = board_data.user_ans_board
    hint_board = board_data.hint_board
    x = board_data.x
    y = board_data.y
    
    mask = Image.new("RGBA", IMGSIZE, color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(mask, 'RGBA')

    # 計算所在的3x3方格的起點
    box_start_x = MARGIN + (x // 3) * 3 * CELL_SIZE
    box_start_y = MARGIN + (y // 3) * 3 * CELL_SIZE
    box_rect = [
        box_start_x,
        box_start_y,
        box_start_x + 3 * CELL_SIZE,
        box_start_y + 3 * CELL_SIZE
    ]

    # 計算所在行和列的起點
    cell_start_x = MARGIN + x * CELL_SIZE
    cell_start_y = MARGIN + y * CELL_SIZE
    row_rect = [
        MARGIN,
        cell_start_y,
        MARGIN + GRID_SIZE,
        cell_start_y + CELL_SIZE
    ]
    col_rect = [
        cell_start_x,
        MARGIN,
        cell_start_x + CELL_SIZE,
        MARGIN + GRID_SIZE
    ]
    cell_rect = [
        cell_start_x,
        cell_start_y,
        cell_start_x + CELL_SIZE,
        cell_start_y + CELL_SIZE
    ]

    
    draw.rectangle(box_rect, fill = HIGHLIGHT_COLOR[0]) # 標示3x3方格
    draw.rectangle(row_rect, fill = HIGHLIGHT_COLOR[0]) # 標示row
    draw.rectangle(col_rect, fill = HIGHLIGHT_COLOR[0]) # 標示col
    draw.rectangle(cell_rect, fill = HIGHLIGHT_COLOR[1]) #標示cell
    
    temp_board = [[0]*9 for i in range(9)]
    for row in range(9): #merge user_ans_board, hint_board and default_board
        for col in range(9):
            temp_board[row][col] = board[row][col] + user_ans_board[row][col] + hint_board[row][col]
            
    for row in range(9):
        for col in range(9):
            if temp_board[row][col] == temp_board[y][x] and temp_board[row][col] and (row != y or col != x):
                cell_start_x = MARGIN + col * CELL_SIZE
                cell_start_y = MARGIN + row * CELL_SIZE
                draw.rectangle( #標示同數字的cell
                    [
                        cell_start_x,
                        cell_start_y,
                        cell_start_x + CELL_SIZE,
                        cell_start_y + CELL_SIZE        
                    ],
                    fill = HIGHLIGHT_COLOR[2]
                )
    
    image = Image.alpha_composite(image, mask)

    return image

if __name__ == "__main__":
    output_path = "./temp/correct.gif"
    duration = 66

    board = [[9, 0, 0, 0, 0, 0, 0, 0, 2], [0, 0, 3, 7, 0, 9, 8, 0, 0], [0, 0, 4, 3, 6, 0, 1, 0, 0], [1, 0, 6, 0, 0, 0, 2, 0, 8], [0, 0, 9, 0, 4, 0, 7, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 7, 1, 3, 0, 6, 0, 0], [0, 0, 2, 6, 0, 5, 9, 0, 0], [3, 0, 0, 0, 0, 0, 0, 0, 7]]
    board_data = {
        "board": board,
        "user_ans_board": [[0]*9 for i in range(9)],
        "hint_board": [[0]*9 for i in range(9)],
        "x": 0,
        "y": 0
    }
    board_img = draw_board(BoardData(board_data))
    images = drawCorrectAni(board_img)
    images[0].save(output_path, save_all=True, append_images=images[1:], duration=duration)