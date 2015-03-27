import simplecanvas as sc
import time
import game
import draw

draw.sc = sc
CELL_SPACING = draw.타일간격
sc.init((2+CELL_SPACING*4-1,2+CELL_SPACING*4-1+16),4)

is_moving = True
moving_start_time = time.time()

def draw_board(board):
    global is_moving
    last_step = False
    if is_moving:
        TIME_STEP1 = 0.1
        TIME_STEP2 = 0.08
        dt = (time.time()-moving_start_time) / TIME_STEP1
        if time.time() - moving_start_time > TIME_STEP1+TIME_STEP2:
            is_moving = False
        elif time.time() - moving_start_time > TIME_STEP1:
            last_step = True
    for x in range(4):
        for y in range(4):
            if board[y*4+x]:
                if last_step:
                    if len(board[y*4+x][1]) >= 2:
                        #draw_cell(x,y,board[y*4+x][0], enlarge=True)
                        draw.____find_and_call_function([
                            ('EXPR', x),
                            ('EXPR', y),
                            ('NAME', '에'),
                            ('EXPR', board[y*4+x][0]),
                            ('NAME', '타일'),
                            ('NAME', '그리기'),
                            ('EXPR', True),
                            ('EXPR', False),
                            ], locals(), draw.__dict__, draw.____functions)
                    elif board[y*4+x][1] == [-1]:
                        #draw_cell(x,y,board[y*4+x][0], appear=True)
                        draw.____find_and_call_function([
                            ('EXPR', x),
                            ('EXPR', y),
                            ('NAME', '에'),
                            ('EXPR', board[y*4+x][0]),
                            ('NAME', '타일'),
                            ('NAME', '그리기'),
                            ('EXPR', False),
                            ('EXPR', True),
                            ], locals(), draw.__dict__, draw.____functions)
                    else:
                        draw.____find_and_call_function([
                            ('EXPR', x),
                            ('EXPR', y),
                            ('NAME', '에'),
                            ('EXPR', board[y*4+x][0]),
                            ('NAME', '타일'),
                            ('NAME', '그리기'),
                            ('EXPR', False),
                            ('EXPR', False),
                            ], locals(), draw.__dict__, draw.____functions)
                elif is_moving:
                    if len(board[y*4+x][1]) >= 2:
                        for p in board[y*4+x][1]:
                            fx = (p-1)%4
                            fy = (p-1)//4
                            dx = (x-fx)*dt
                            dy = (y-fy)*dt
                            #draw_cell(fx,fy,board[y*4+x][0]//2, dx, dy)
                            draw.____find_and_call_function([
                                ('EXPR', fx+dx),
                                ('EXPR', fy+dy),
                                ('NAME', '에'),
                                ('EXPR', board[y*4+x][0]//2),
                                ('NAME', '타일'),
                                ('NAME', '그리기'),
                                ('EXPR', False),
                                ('EXPR', False),
                                ], locals(), draw.__dict__, draw.____functions)
                    elif board[y*4+x][1] == [-1]:
                        pass
                    else:
                        fx = (board[y*4+x][1][0]-1)%4
                        fy = (board[y*4+x][1][0]-1)//4
                        dx = (x-fx)*dt
                        dy = (y-fy)*dt
                        #draw_cell(fx,fy,board[y*4+x][0], dx, dy)
                        draw.____find_and_call_function([
                            ('EXPR', fx+dx),
                            ('EXPR', fy+dy),
                            ('NAME', '에'),
                            ('EXPR', board[y*4+x][0]),
                            ('NAME', '타일'),
                            ('NAME', '그리기'),
                            ('EXPR', False),
                            ('EXPR', False),
                            ], locals(), draw.__dict__, draw.____functions)
                else:
                    #draw_cell(x,y,board[y*4+x][0])
                    draw.____find_and_call_function([
                        ('EXPR', x),
                        ('EXPR', y),
                        ('NAME', '에'),
                        ('EXPR', board[y*4+x][0]),
                        ('NAME', '타일'),
                        ('NAME', '그리기'),
                        ('EXPR', False),
                        ('EXPR', False),
                        ], locals(), draw.__dict__, draw.____functions)

board = game.____find_and_call_function([('NAME', '새'), ('NAME', '게임'), ('NAME', '준비')], locals(), game.__dict__, game.____functions)

def keydown(key, mod):
    global is_moving, moving_start_time
    if is_moving:
        return
    ret = False
    if key == 273: #up
        ret = game.____find_and_call_function([('NAME', 'board'), ('NAME', '위로')], dict(board=board), game.__dict__, game.____functions)
    elif key == 274: #down
        ret = game.____find_and_call_function([('NAME', 'board'), ('NAME', '아래로')], dict(board=board), game.__dict__, game.____functions)
    elif key == 275: #right
        ret = game.____find_and_call_function([('NAME', 'board'), ('NAME', '오른쪽으로')], dict(board=board), game.__dict__, game.____functions)
    elif key == 276: #left
        ret = game.____find_and_call_function([('NAME', 'board'), ('NAME', '왼쪽으로')], dict(board=board), game.__dict__, game.____functions)
    if ret:
        game.____find_and_call_function([('NAME', 'board'), ('NAME', '랜덤'), ('NAME', '생성')], dict(board=board), game.__dict__, game.____functions)
        moving_start_time = time.time()
        is_moving = True
        # turn += 1

def update():
    if is_moving:
        sc.clear((0,0,0))
        draw_board(board)

sc.mainloop(update, onKeyDown = keydown)
