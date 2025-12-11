class Piece:
    def __init__(self, color):
        self.color = color
        self.has_moved = False


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)

    def get_moves(self, board, r, c):
        moves = []
        if self.color == "white":
            dr, start = -1, 6
            enemy = 'black'
        else:
            dr, start = 1, 1
            enemy = "white"
         # Di chuyển 1 ô hoặc 2 ô nếu ở hàng xuất phát
        if 0 <= r+dr < 8 and board.board[r+dr][c] is None:
            moves.append((r+dr, c))  # danh sáchh các bước đi hợp lệ
            if r == start and board.board[r+2*dr][c] is None:
                moves.append((r+2*dr, c))
        # Ăn chéo
        for dc in (-1, 1):  # phía trái -1 or phải 1
            # tính vị trí mới khi di chuyển 1 bước chéo
            nr, nc = r+dr, c+dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board.board[nr][nc]
                if target and target.color == enemy:
                    moves.append((nr, nc))
        return moves


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)

    def get_moves(self, board, r, c):
        moves = []
        # Đi theo 4 hướng: lên, xuống, trái, phải
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                if board.board[nr][nc] is None:
                    moves.append((nr, nc))
                else:
                    if board.board[nr][nc].color != self.color:
                        moves.append((nr, nc))
                    break
                nr += dr
                nc += dc
        return moves


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)

    def get_moves(self, board, r, c):
        moves = []
        # 8 nước có thể của mã
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            nr, nc = r+dr, c+dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board.board[nr][nc]
                if target is None or target.color != self.color:
                    moves.append((nr, nc))
        return moves


class Bishop (Piece):
    def __init__(self, color):
        super().__init__(color)

    def get_moves(self, board, r, c):
        moves = []
        dirs = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                if board.board[nr][nc] is None:
                    moves.append((nr, nc))
                else:
                    if board.board[nr][nc].color != self.color:
                        moves.append((nr, nc))
                    break
                nr += dr
                nc += dc
        return moves


class King(Piece):
    def __init__(self, color):
        super().__init__(color)

    def get_moves(self, board, r, c, _is_checking_attack=False):
        moves = []

        enemy_color = 'black' if self.color == 'white' else 'white'
        # Vua đi 1 ô mọi hướng  tính nhập thành)
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1),
                (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board.board[nr][nc]
                if target is None or target.color != self.color:
                    moves.append((nr, nc))

        # --- LOGIC NHẬP THÀNH ---
        if not _is_checking_attack and not self.has_moved and not board.is_in_check(self.color):

            # 1. Nhập thành cánh Vua (bên phải)
            rook_right = board.board[r][7]
            if isinstance(rook_right, Rook) and not rook_right.has_moved:
                # Kiểm tra các ô ở giữa có trống không
                if board.board[r][5] is None and board.board[r][6] is None:
                    # Kiểm tra các ô Vua đi qua có bị tấn công không
                    if not board.is_square_attacked((r, 5), enemy_color) and \
                            not board.is_square_attacked((r, 6), enemy_color):
                        moves.append((r, 6))

        # 2. Nhập thành cánh Hậu (bên trái)
            rook_left = board.board[r][0]
            if isinstance(rook_left, Rook) and not rook_left.has_moved:
                # Kiểm tra các ô ở giữa có trống không
                if board.board[r][1] is None and board.board[r][2] is None and board.board[r][3] is None:
                    # Kiểm tra các ô Vua đi qua có bị tấn công không
                    if not board.is_square_attacked((r, 2), enemy_color) and \
                            not board.is_square_attacked((r, 3), enemy_color):
                        moves.append((r, 2))

        return moves


class Queen (Piece):
    def __init__(self, color):
        super(). __init__(color)

    def get_moves(self, board, r, c):
        moves = []
        dirs = [(1, 1), (1, -1), (-1, 1), (-1, -1),
                (-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                if board.board[nr][nc] is None:
                    moves.append((nr, nc))
                else:
                    if board.board[nr][nc].color != self.color:
                        moves.append((nr, nc))
                    break
                nr += dr
                nc += dc
        return moves