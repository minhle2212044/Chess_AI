# Sources/Gameplay/board.py

from Gameplay.move import Pawn, Knight, Bishop, Rook, Queen, King
from Gameplay.rule import (
    is_in_check,
    is_square_attacked,
    is_stalemate,
    is_checkmate,
    insufficient_material
)

class Board:
    def __init__(self):
        # Bàn cờ 8×8
        self.board = [[None for _ in range(8)] for _ in range(8)]

        # --- Đặt quân đen ---
        self.board[0] = [
            Rook('black'), Knight('black'), Bishop('black'), Queen('black'),
            King('black'), Bishop('black'), Knight('black'), Rook('black')
        ]
        for c in range(8):
            self.board[1][c] = Pawn('black')

        # --- Đặt quân trắng ---
        self.board[7] = [
            Rook('white'), Knight('white'), Bishop('white'), Queen('white'),
            King('white'), Bishop('white'), Knight('white'), Rook('white')
        ]
        for c in range(8):
            self.board[6][c] = Pawn('white')

        # --- Cho các luật nâng cao ---
        self.en_passant_square = None
        self.last_move = None

        # NEW – cho threefold + 50 move rule
        self.position_history = []
        self.halfmove_clock = 0

    # ---------------------------------------------------------
    # Vị trí vua
    # ---------------------------------------------------------
    def get_king_position(self, color):
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if isinstance(p, King) and p.color == color:
                    return (r, c)
        return None

    # ---------------------------------------------------------
    # Wrapper rule
    # ---------------------------------------------------------
    def is_square_attacked(self, pos, attacker_color):
        return is_square_attacked(self, pos, attacker_color)

    def is_in_check(self, color):
        return is_in_check(self, color)

    # ---------------------------------------------------------
    # Sinh FEN rút gọn
    # ---------------------------------------------------------
    def simple_fen(self, turn_color="white"):
        fen = ""
        for r in range(8):
            empty = 0
            for c in range(8):
                p = self.board[r][c]
                if p is None:
                    empty += 1
                else:
                    if empty > 0:
                        fen += str(empty)
                        empty = 0
                    letter = ""
                    if isinstance(p, Pawn):   letter = "p"
                    elif isinstance(p, Knight): letter = "n"
                    elif isinstance(p, Bishop): letter = "b"
                    elif isinstance(p, Rook):   letter = "r"
                    elif isinstance(p, Queen):  letter = "q"
                    elif isinstance(p, King):   letter = "k"
                    if p.color == "white":
                        letter = letter.upper()
                    fen += letter

            if empty > 0:
                fen += str(empty)
            if r < 7:
                fen += "/"

        fen += " w" if turn_color == "white" else " b"
        return fen

    # ---------------------------------------------------------
    # Di chuyển quân
    # ---------------------------------------------------------
    def move_piece(self, move):
        (r1, c1), (r2, c2) = move
        p = self.board[r1][c1]

        captured_piece = self.board[r2][c2]  # để xét 50-move rule
        p.has_moved = True

        # 1. Nhập thành
        if isinstance(p, King) and abs(c1 - c2) == 2:
            self.board[r2][c2] = p
            self.board[r1][c1] = None

            if c2 > c1:
                rook = self.board[r1][7]
                rook.has_moved = True
                self.board[r1][5] = rook
                self.board[r1][7] = None
            else:
                rook = self.board[r1][0]
                rook.has_moved = True
                self.board[r1][3] = rook
                self.board[r1][0] = None

        # 2. Phong cấp
        elif isinstance(p, Pawn) and (r2 == 0 or r2 == 7):
            self.board[r2][c2] = Queen(p.color)
            self.board[r1][c1] = None

        # 3. Di chuyển thường
        else:
            self.board[r2][c2] = p
            self.board[r1][c1] = None

        # --- UPDATE HALF-MOVE CLOCK (50-move rule) ---
        if isinstance(p, Pawn) or captured_piece is not None:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # Lưu nước đi
        self.last_move = move

    # ---------------------------------------------------------
    # Lấy toàn bộ nước đi hợp lệ
    # ---------------------------------------------------------
    def get_all_moves(self, color):
        moves = []

        # sinh nước đi thô
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p and p.color == color:
                    for dest in p.get_moves(self, r, c):
                        moves.append(((r, c), dest))

        # lọc nước hợp lệ
        legal = []
        import copy
        for mv in moves:
            newb = copy.deepcopy(self)
            newb.move_piece(mv)
            if not newb.is_in_check(color):
                legal.append(mv)

        return legal

    # ---------------------------------------------------------
    # Evaluate đơn giản
    # ---------------------------------------------------------
    def evaluate(self):
        score = 0
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if not p: continue
                val = 1 if isinstance(p, Pawn) else \
                      3 if isinstance(p, (Knight, Bishop)) else \
                      5 if isinstance(p, Rook) else \
                      9 if isinstance(p, Queen) else 0
                score += val if p.color == "white" else -val
        return score

    # ---------------------------------------------------------
    # Evaluate trung tâm
    # ---------------------------------------------------------
    def evaluate_1(self):
        score = 0
        piece_val = {Pawn:1, Knight:3, Bishop:3, Rook:5, Queen:9, King:0}

        center = [(4,2),(4,3),(4,4),(4,5),(3,2),(3,3),(3,4),(3,5)]

        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if not p: continue

                value = piece_val[type(p)]
                bonus = 0.3 if (r,c) in center else 0

                attack = 0
                enemy = "black" if p.color=="white" else "white"
                for (nr,nc) in p.get_moves(self,r,c):
                    t = self.board[nr][nc]
                    if t and t.color==enemy: attack += 0.2

                score += (value+bonus+attack) if p.color=="white" else -(value+bonus+attack)

        if self.is_in_check("white"): score -= 0.5
        if self.is_in_check("black"): score += 0.5
        return score

    # ---------------------------------------------------------
    # Evaluate nâng cao
    # ---------------------------------------------------------
    def evaluate_2(self):
        score = 0
        piece_val = {Pawn:1, Knight:3, Bishop:3, Rook:5, Queen:9, King:0}

        center = [(4,2),(4,3),(4,4),(4,5),(3,2),(3,3),(3,4),(3,5)]
        near   = [(5,2),(5,3),(5,4),(5,5),(2,2),(2,3),(2,4),(2,5)]

        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if not p: continue

                value = piece_val[type(p)]
                bonus = 0.4 if (r,c) in center else (0.2 if (r,c) in near else 0)

                moves = p.get_moves(self,r,c)
                atk = 0
                enemy = "black" if p.color=="white" else "white"
                for (nr,nc) in moves:
                    t = self.board[nr][nc]
                    if t and t.color==enemy: atk += 0.25

                mobility = len(moves)*0.1
                total = value + bonus + atk + mobility

                score += total if p.color=="white" else -total

        if self.is_in_check("white"): score -= 0.6
        if self.is_in_check("black"): score += 0.6
        return score
