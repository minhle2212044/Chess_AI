import copy
import math

def minimax(board, depth, alpha, beta, maximizing):
    # Nếu đã đạt độ sâu tối đa hoặc game kết thúc
    if depth == 0:
        return board.evaluate(), None
    if maximizing:  # true la trang flase là đen
        moves = board.get_all_moves('white')
        if not moves:
            # Nếu trắng không còn nước đi
            if board.is_in_check('white'):
                return -math.inf, None  # trắng bị chiếu hết
            else:
                return 0, None  # hòa
        maxv, best_move = -math.inf, None  # gia tri max white dat dc
        for m in moves:
            newb = copy.deepcopy(board)
            newb.move_piece(m)
            # val giá trị đánh giá điểm
            val, _ = minimax(newb, depth-1, alpha, beta, False)
            if val > maxv:
                maxv, best_move = val, m
            alpha = max(alpha, maxv)
            if beta <= alpha:
                break
        return maxv, best_move
    else:
        moves = board.get_all_moves('black')
        if not moves:
            if board.is_in_check('black'):
                return math.inf, None
            else:
                return 0, None
        minv, best_move = math.inf, None
        for m in moves:
            newb = copy.deepcopy(board)
            newb.move_piece(m)
            val, _ = minimax(newb, depth-1, alpha, beta, True)
            if val < minv:
                minv, best_move = val, m
            beta = min(beta, minv)
            if beta <= alpha:
                break
        return minv, best_move
