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

        # --- Cho luật nâng cao ---
        self.en_passant_square = None
        self.last_move = None

    # ---------------------------------------------------------
    # Tìm vị trí vua
    # ---------------------------------------------------------
    def get_king_position(self, color):
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if isinstance(p, King) and p.color == color:
                    return (r, c)
        return None

    # ---------------------------------------------------------
    # Wrapper gọi rule.py
    # ---------------------------------------------------------
    def is_square_attacked(self, pos, attacker_color):
        return is_square_attacked(self, pos, attacker_color)

    def is_in_check(self, color):
        return is_in_check(self, color)

    # ---------------------------------------------------------
    # Di chuyển quân
    # ---------------------------------------------------------
    def move_piece(self, move):
        (r1, c1), (r2, c2) = move
        p = self.board[r1][c1]

        # đánh dấu đã di chuyển (quan trọng cho castle)
        p.has_moved = True

        # --------------------------------------------
        # 1. Nhập thành
        # --------------------------------------------
        if isinstance(p, King) and abs(c1 - c2) == 2:
            # di chuyển vua
            self.board[r2][c2] = p
            self.board[r1][c1] = None

            # di chuyển xe
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

        # --------------------------------------------
        # 2. Phong cấp
        # --------------------------------------------
        elif isinstance(p, Pawn) and (r2 == 0 or r2 == 7):
            self.board[r2][c2] = Queen(p.color)
            self.board[r1][c1] = None

        # --------------------------------------------
        # 3. Di chuyển thông thường
        # --------------------------------------------
        else:
            self.board[r2][c2] = p
            self.board[r1][c1] = None

        # LƯU LẠI NƯỚC ĐI (cần cho en-passant sau này)
        self.last_move = (r1, c1), (r2, c2)

    # ---------------------------------------------------------
    # Lấy tất cả nước đi hợp lệ
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

        # lọc nước đi hợp lệ (không để mình bị chiếu)
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
                if p:
                    val = 0
                    if isinstance(p, Pawn):
                        val = 1
                    elif isinstance(p, Knight):
                        val = 3
                    elif isinstance(p, Bishop):
                        val = 3
                    elif isinstance(p, Rook):
                        val = 5
                    elif isinstance(p, Queen):
                        val = 9

                    if p.color == 'white':
                        score += val
                    else:
                        score -= val
        return score

    # ---------------------------------------------------------
    # Evaluate trung tâm + tấn công
    # ---------------------------------------------------------
    def evaluate_1(self):
        score = 0
        piece_value = {
            Pawn: 1, Knight: 3, Bishop: 3, Rook: 5, Queen: 9, King: 0
        }

        center = [(4, 2), (4, 3), (4, 4), (4, 5),
                  (3, 2), (3, 3), (3, 4), (3, 5)]

        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if not p:
                    continue

                value = piece_value[type(p)]
                center_bonus = 0.3 if (r, c) in center else 0

                attack_bonus = 0
                enemy = 'black' if p.color == 'white' else 'white'
                for (nr, nc) in p.get_moves(self, r, c):
                    target = self.board[nr][nc]
                    if target and target.color == enemy:
                        attack_bonus += 0.2

                if p.color == 'white':
                    score += value + center_bonus + attack_bonus
                else:
                    score -= value + center_bonus + attack_bonus

        if self.is_in_check('white'):
            score -= 0.5
        if self.is_in_check('black'):
            score += 0.5

        return score

    # ---------------------------------------------------------
    # Evaluate nâng cao hơn
    # ---------------------------------------------------------
    def evaluate_2(self):
        score = 0
        piece_value = {
            Pawn: 1, Knight: 3, Bishop: 3, Rook: 5, Queen: 9, King: 0
        }

        center = [(4, 2), (4, 3), (4, 4), (4, 5),
                  (3, 2), (3, 3), (3, 4), (3, 5)]

        near_center = [(5, 2), (5, 3), (5, 4), (5, 5),
                       (2, 2), (2, 3), (2, 4), (2, 5)]

        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if not p:
                    continue

                value = piece_value[type(p)]
                center_bonus = 0.4 if (r, c) in center else (0.2 if (r, c) in near_center else 0)

                moves = p.get_moves(self, r, c)
                mobility_bonus = len(moves) * 0.1

                attack_bonus = 0
                enemy = 'black' if p.color == 'white' else 'white'
                for (nr, nc) in moves:
                    target = self.board[nr][nc]
                    if target and target.color == enemy:
                        attack_bonus += 0.25

                total = value + center_bonus + mobility_bonus + attack_bonus

                if p.color == 'white':
                    score += total
                else:
                    score -= total

        if self.is_in_check('white'):
            score -= 0.6
        if self.is_in_check('black'):
            score += 0.6

        return score
