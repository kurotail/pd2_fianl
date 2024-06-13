from PIL import Image, ImageDraw, ImageFont

BG_COLOR = "#232428"
GRIDBG_COLOR = ["#383a40", "#2e3035"]
LINE_COLOR = "#dbdee1"
DEFAULT_NUM_COLOR = "#dbdee1"
HIGHLIGHT_COLOR = [
    (255, 255, 255, 50), #box, row, col highlight color
    (175, 211, 243, 100), #selected cell highlight color
    (213, 243, 175, 100) #same number cell highlight color
]

IMGSIZE = (500, 500)
MARGIN = 10

GRID_SIZE = IMGSIZE[0] - 2 * MARGIN
CELL_SIZE = GRID_SIZE // 9

def draw_board(board:list) -> Image:
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
            if board[row][col]:
                number = str(board[row][col])
                bbox = font.getbbox(number)
                text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                text_x = start_x + col * CELL_SIZE + (CELL_SIZE - text_width) // 2
                text_y = start_y + row * CELL_SIZE + (CELL_SIZE - text_height) // 2
                draw.text((text_x+1, text_y-3), number, fill=DEFAULT_NUM_COLOR, font=font)

    return image

def highlight_board(board:list, x:int, y:int, image:Image) -> Image:
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
    
    for row in range(9):
        for col in range(9):
            if board[row][col] == board[y][x] and board[row][col] and row != y and col != x:
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