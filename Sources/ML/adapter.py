# ML/adapter.py
import chess
from Gameplay.move import Pawn, Knight, Bishop, Rook, Queen, King

def to_chess_board(board_obj, current_color):
    """
    Convert custom Board() → python-chess Board()
    WITHOUT relying on board_obj.turn_color
    """
    b = chess.Board(None)
    b.clear_board()

    for r in range(8):
        for c in range(8):
            p = board_obj.board[r][c]
            if p is None:
                continue
            
            square = chess.square(c, 7 - r)

            if isinstance(p, Pawn):
                pt = chess.PAWN
            elif isinstance(p, Knight):
                pt = chess.KNIGHT
            elif isinstance(p, Bishop):
                pt = chess.BISHOP
            elif isinstance(p, Rook):
                pt = chess.ROOK
            elif isinstance(p, Queen):
                pt = chess.QUEEN
            elif isinstance(p, King):
                pt = chess.KING

            color = chess.WHITE if p.color == "white" else chess.BLACK
            b.set_piece_at(square, chess.Piece(pt, color))

    # Set turn based on main.py
    b.turn = chess.WHITE if current_color == "white" else chess.BLACK
    return b


def from_uci_move(uci):
    """
    Convert UCI string to ((r1,c1),(r2,c2))
    """
    c1 = ord(uci[0]) - 97
    r1 = 8 - int(uci[1])

    c2 = ord(uci[2]) - 97
    r2 = 8 - int(uci[3])

    return (r1, c1), (r2, c2)
