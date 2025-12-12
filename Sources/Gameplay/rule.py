# rule.py – xử lý toàn bộ luật cờ vua cấp cao

from Gameplay.move import King, Pawn, Rook, Bishop, Knight, Queen

# ------------------------------------------------------------
# 1. Tìm vị trí vua
# ------------------------------------------------------------
def find_king(board, color):
    for r in range(8):
        for c in range(8):
            p = board.board[r][c]
            if isinstance(p, King) and p.color == color:
                return (r, c)
    return None

# ------------------------------------------------------------
# 2. Ô bị tấn công
# ------------------------------------------------------------
def is_square_attacked(board, pos, attacker_color):
    r0, c0 = pos

    for r in range(8):
        for c in range(8):
            p = board.board[r][c]
            if p and p.color == attacker_color:

                if isinstance(p, King):
                    moves = p.get_moves(board, r, c, _is_checking_attack=True)
                else:
                    moves = p.get_moves(board, r, c)

                if pos in moves:
                    return True

    return False

# ------------------------------------------------------------
# 3. Chiếu
# ------------------------------------------------------------
def is_in_check(board, color):
    king_pos = find_king(board, color)
    if not king_pos:
        return True
    enemy = "black" if color == "white" else "white"
    return is_square_attacked(board, king_pos, enemy)

# ------------------------------------------------------------
# 4. Checkmate
# ------------------------------------------------------------
def is_checkmate(board, color):
    if not is_in_check(board, color):
        return False
    return len(board.get_all_moves(color)) == 0

# ------------------------------------------------------------
# 5. Stalemate
# ------------------------------------------------------------
def is_stalemate(board, color):
    if is_in_check(board, color):
        return False
    return len(board.get_all_moves(color)) == 0

# ------------------------------------------------------------
# 6. Insufficient material
# ------------------------------------------------------------
def insufficient_material(board):
    pieces = []
    for r in range(8):
        for c in range(8):
            p = board.board[r][c]
            if p:
                pieces.append(p)

    # King vs King
    if len(pieces) == 2:
        return True

    # King + minor vs King
    if len(pieces) == 3:
        for p in pieces:
            if isinstance(p, (Bishop, Knight)):
                return True

    # 2 tượng cùng màu ô
    if len(pieces) == 4:
        bishops = [p for p in pieces if isinstance(p, Bishop)]
        if len(bishops) == 2:
            cols = []
            for r in range(8):
                for c in range(8):
                    if isinstance(board.board[r][c], Bishop):
                        cols.append((r + c) % 2)
            if cols[0] == cols[1]:
                return True

    return False

# ------------------------------------------------------------
# 7. Threefold repetition
# ------------------------------------------------------------
def threefold_repetition(board):
    if not hasattr(board, "position_history"):
        return False

    if len(board.position_history) < 3:
        return False

    last = board.position_history[-1]
    return board.position_history.count(last) >= 3

# ------------------------------------------------------------
# 8. Fifty-move rule
# ------------------------------------------------------------
def fifty_move_rule(board):
    return hasattr(board, "halfmove_clock") and board.halfmove_clock >= 100
