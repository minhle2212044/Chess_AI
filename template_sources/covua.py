# -*- coding: utf-8 -*-
# King (Vua)

# Queen pyth(Hậu)

# Rook (Xe)

# Bishop (Tượng)

# Knight (Mã)

# Pawn (Tốt)
import random
import copy
import sys
import pygame
import math
running = True


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


class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.board[0] = [Rook('black'), Knight('black'), Bishop('black'),
                         Queen('black'), King('black'), Bishop('black'), Knight('black'), Rook('black')]
        for c in range(8):
            self.board[1][c] = Pawn('black')
        # Đặt quân trắng ở hàng 6-7
        self.board[7] = [Rook('white'), Knight('white'), Bishop('white'),
                         Queen('white'), King('white'), Bishop('white'), Knight('white'), Rook('white')]
        for c in range(8):
            self.board[6][c] = Pawn('white')

    def get_king_position(self, color):
        # Tìm vị trí vua của màu chỉ định
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if isinstance(p, King) and p.color == color:
                    return (r, c)
        return None

    def is_square_attacked(self, pos, attacker_color):
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p and p.color == attacker_color:
                    # Xử lý đặc biệt cho Vua để tránh đệ quy vô hạn
                    if isinstance(p, King):
                        # Gọi get_moves với cờ đặc biệt để chỉ lấy các nước đi cơ bản
                        if pos in p.get_moves(self, r, c, _is_checking_attack=True):
                            return True
                    else:
                        if pos in p.get_moves(self, r, c):
                            return True
        return False

    def is_in_check(self, color):
        # Kiểm tra xem màu chỉ định có bị chiếu (có bị đe dọa bởi quân địch) không
        pos = self.get_king_position(color)
        if pos is None:
            return True
        enemy = 'black' if color == 'white' else 'white'
        return self.is_square_attacked(pos, enemy)

    def move_piece(self, move):
        # Thực hiện di chuyển (và phong cấp nếu pawn tới cuối bàn)
        (r1, c1), (r2, c2) = move  # xuất phát và đích
        p = self.board[r1][c1]

        # Đánh dấu quân cờ đã di chuyển
        p.has_moved = True

        # Xử lý nhập thành
        if isinstance(p, King) and abs(c1 - c2) == 2:
            # Di chuyển Vua
            self.board[r2][c2] = p
            self.board[r1][c1] = None
            # Di chuyển Xe
            if c2 > c1:  # Nhập thành cánh Vua (phải)
                rook = self.board[r1][7]
                rook.has_moved = True
                self.board[r1][5] = rook
                self.board[r1][7] = None
            else:  # Nhập thành cánh Hậu (trái)
                rook = self.board[r1][0]
                rook.has_moved = True
                self.board[r1][3] = rook
                self.board[r1][0] = None

        # Phong cấp pawn
        elif isinstance(p, Pawn) and (r2 == 0 or r2 == 7):
            self.board[r2][c2] = Queen(p.color)
            self.board[r1][c1] = None
        else:  # Di chuyển bình thường
            self.board[r2][c2] = p
            self.board[r1][c1] = None

    def get_all_moves(self, color):
        # Sinh tất cả nước đi (hợp lệ) của một màu
        moves = []
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p and p.color == color:
                    for dest in p.get_moves(self, r, c):
                        moves.append(((r, c), dest))
        # Lọc bớt các nước đi khiến chính mình bị chiếu
        legal = []
        import copy
        for move in moves:
            newb = copy.deepcopy(self)  # tao bản sao bàn cờ hiện tại
            newb.move_piece(move)
            if not newb.is_in_check(color):
                legal.append(move)
        return legal

    def evaluate(self):
        # Hàm đánh giá: tổng điểm trắng trừ điểm đen
        score = 0
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p:
                    v = 0
                    if isinstance(p, Pawn):
                        v = 1
                    elif isinstance(p, Knight):
                        v = 3
                    elif isinstance(p, Bishop):
                        v = 3
                    elif isinstance(p, Rook):
                        v = 5
                    elif isinstance(p, Queen):
                        v = 9
                    # King bỏ qua vì chiếu tướng mới kết thúc
                    if p.color == 'white':
                        score += v
                    else:
                        score -= v
        return score
    # Hàm heuristic 2

    def evaluate_1(self):
        score = 0

       # Giá trị vật chất của các quân cờ
        piece_value = {
            Pawn: 1,
            Knight: 3,
            Bishop: 3,
            Rook: 5,
            Queen: 9,
            King: 0  # Bỏ qua Vua vì chiếu hết quyết định kết thúc
        }

        # Tọa độ: C4=(4,2), D4=(4,3), E4=(4,4), F4=(4,5), C5=(3,2), D5=(3,3), E5=(3,4), F5=(3,5)
        center_squares = [(4, 2), (4, 3), (4, 4), (4, 5),
                          (3, 2), (3, 3), (3, 4), (3, 5)]

        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p:
                    # Giá trị vật chất
                    value = piece_value[type(p)]

                    # Ưu tiên kiểm soát trung tâm
                    center_bonus = 0
                    if (r, c) in center_squares:
                        center_bonus = 0.3  # Thưởng 0.3 điểm cho quân ở trung tâm

                    # Ưu tiên tấn công: Đếm số quân địch bị đe dọa bởi quân này
                    attack_bonus = 0
                    enemy_color = 'black' if p.color == 'white' else 'white'
                    for dest in p.get_moves(self, r, c):
                        target = self.board[dest[0]][dest[1]]
                        if target and target.color == enemy_color:
                            attack_bonus += 0.2  # Thưởng 0.2 điểm cho mỗi quân địch bị đe dọa
                    # Cộng/trừ điểm theo màu
                    if p.color == 'white':
                        score += value + center_bonus + attack_bonus
                    else:
                        score -= value + center_bonus + attack_bonus

        # Ưu tiên chiếu vua
        if self.is_in_check('white'):
            score -= 0.5  # Trừ điểm nếu trắng bị chiếu
        if self.is_in_check('black'):
            score += 0.5  # Cộng điểm nếu đen bị chiếu

        return score

    # Hàm heuristic 3
    def evaluate_2(self):
        # Đoạn này gần giống với heuristic của Vi
        score = 0
        piece_value = {
            Pawn: 1,
            Knight: 3,
            Bishop: 3,
            Rook: 5,
            Queen: 9,
            King: 0
        }
        center_squares = [(4, 2), (4, 3), (4, 4), (4, 5),
                          (3, 2), (3, 3), (3, 4), (3, 5)]
        near_center_squares = [(5, 2), (5, 3), (5, 4),
                               (5, 5), (2, 2), (2, 3), (2, 4), (2, 5)]
        # Đếm số quân bị đe dọa và tính linh hoạt
        white_threats = 0
        black_threats = 0
        white_mobility = 0
        black_mobility = 0
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p:
                    # Giá trị vật chất
                    value = piece_value[type(p)]
                    # Kiểm soát trung tâm và gần trung tâm
                    center_bonus = 0
                    if (r, c) in center_squares:
                        center_bonus = 0.4  # Thưởng nhiều hơn cho trung tâm
                    elif (r, c) in near_center_squares:
                        center_bonus = 0.2  # Thưởng ít hơn cho vùng gần trung tâm
                    # Tính linh hoạt (mobility) và đe dọa
                    attack_bonus = 0
                    moves = p.get_moves(self, r, c)
                    move_count = len(moves)
                    enemy_color = 'black' if p.color == 'white' else 'white'
                    for dest in moves:
                        target = self.board[dest[0]][dest[1]]
                        if target and target.color == enemy_color:
                            attack_bonus += 0.25  # Thưởng cho mỗi quân địch bị đe dọa
                    # Cộng điểm linh hoạt
                    mobility_bonus = move_count * 0.1  # Thưởng 0.1 điểm cho mỗi nước đi hợp lệ
                    # Cộng điểm cho bên tương ứng
                    if p.color == 'white':
                        score += value + center_bonus + attack_bonus + mobility_bonus
                        white_threats += attack_bonus
                        white_mobility += move_count
                    else:
                        score -= value + center_bonus + attack_bonus + mobility_bonus
                        black_threats += attack_bonus
                        black_mobility += move_count
        # An toàn Vua
        white_king_pos = self.get_king_position('white')
        black_king_pos = self.get_king_position('black')
        # Phạt nếu Vua ở vị trí nguy hiểm (gần trung tâm hoặc bị đe dọa nhiều)
        if white_king_pos:
            r, c = white_king_pos
            # Phạt nếu Vua ở trung tâm (ít an toàn)
            king_safety = 0
            if (r, c) in center_squares:
                king_safety -= 0.5
            # Phạt nếu Vua bị nhiều quân đe dọa
            attackers = 0
            for r2 in range(8):
                for c2 in range(8):
                    p = self.board[r2][c2]
                    if p and p.color == 'black':
                        if white_king_pos in p.get_moves(self, r2, c2):
                            attackers += 1
            king_safety -= attackers * 0.3
            score += king_safety
        if black_king_pos:
            r, c = black_king_pos
            king_safety = 0
            if (r, c) in center_squares:
                king_safety -= 0.5
            attackers = 0
            for r2 in range(8):
                for c2 in range(8):
                    p = self.board[r2][c2]
                    if p and p.color == 'white':
                        if black_king_pos in p.get_moves(self, r2, c2):
                            attackers += 1
            king_safety -= attackers * 0.3
            score -= king_safety
        # Ưu tiên chiếu vua
        if self.is_in_check('white'):
            score -= 0.6
        if self.is_in_check('black'):
            score += 0.6
        return score


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


pygame.init()
# Khởi tạo âm thanh
pygame.mixer.init()  # Khởi tạo mixer của pygame để phát âm thanh

# Tải âm thanh di chuyển quân cờ
move_sound = pygame.mixer.Sound("images/music.mp3")  # Tải file âm thanh
WIDTH = 800
HEIGHT = 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess with AI")
font = pygame.font.SysFont(None, 40)
WHITE = (232, 232, 232)
BLACK = (139, 69, 19)
# Biến đồng hồ
font = pygame.font.SysFont(None, 40)
font_1 = pygame.font.SysFont(None, 100)
# Thời gian giới hạn (5 phút)
# Giới hạn thời gian 5 phút (5 * 60 giây * 1000 milliseconds)
time_limit = 10 * 60 * 1000
start_time = pygame.time.get_ticks()  # Thời gian bắt đầu

turn = 'white'
selected = None
valid_moves = []
square = (WIDTH - 160) // 8


def draw_board():
    # Vẽ bàn cờ và quân cờ

    for r in range(8):
        for c in range(8):
            rect = pygame.Rect(c*square, r*square, square, square)
            bg = WHITE if (r+c) % 2 == 0 else BLACK
            pygame.draw.rect(screen, bg, rect)

            # Nếu có bước đi hợp lệ, vẽ ô hợp lệ lên bàn cờ
            if (r, c) in valid_moves:
                # Vẽ nền màu vàng nhạt cho ô hợp lệ (hoặc màu khác nếu muốn)
                # Vẽ viền vàng cho ô hợp lệ
                pygame.draw.rect(screen, (255, 255, 0), rect, 5)

            p = board.board[r][c]
            if p:
                # Xác định ký hiệu quân
                if isinstance(p, Pawn):
                    image_file = f"images/{'white' if p.color == 'white' else 'black'}_pawn.png"
                elif isinstance(p, Knight):
                    image_file = f"images/{'white' if p.color == 'white' else 'black'}_knight.png"
                elif isinstance(p, Bishop):
                    image_file = f"images/{'white' if p.color == 'white' else 'black'}_bishop.png"
                elif isinstance(p, Rook):
                    image_file = f"images/{'white' if p.color == 'white' else 'black'}_rook.png"
                elif isinstance(p, Queen):
                    image_file = f"images/{'white' if p.color == 'white' else 'black'}_queen.png"
                elif isinstance(p, King):
                    image_file = f"images/{'white' if p.color == 'white' else 'black'}_king.png"

                piece_image = pygame.image.load(image_file).convert_alpha()

                # Scale quân tốt nhỏ lại còn 70%
                if isinstance(p, Pawn):
                    piece_image = pygame.transform.scale(
                        piece_image, (int(square * 0.7), int(square * 0.7)))
                    offset_x = (square - piece_image.get_width()) // 2
                    offset_y = (square - piece_image.get_height()) // 2
                else:
                    piece_image = pygame.transform.scale(
                        piece_image, (square, square))
                    offset_x = offset_y = 0

                # Render đổ bóng cho quân cờ (khớp hình dạng)
                shadow = piece_image.copy()
                # Tạo bóng với độ trong suốt
                shadow.fill((0, 0, 0, 100),
                            special_flags=pygame.BLEND_RGBA_MULT)
                # Đổ bóng lệch 5px
                screen.blit(shadow, (rect.x + offset_x +
                            5, rect.y + offset_y + 5))

                # Vẽ quân cờ
                screen.blit(
                    piece_image, (rect.x + offset_x, rect.y + offset_y))
    # Nếu vua bị chiếu, vẽ viền đỏ quanh ô vua
    white_king_pos = board.get_king_position('white')
    black_king_pos = board.get_king_position('black')
    # Kiểm tra nếu vua trắng bị chiếu
    if board.is_in_check('white') and white_king_pos:
        r, c = white_king_pos
        rect = pygame.Rect(c * square, r * square, square, square)
        # Vẽ viền đỏ cho ô vua trắng bị chiếu
        pygame.draw.rect(screen, (255, 0, 0), rect, 5)
        check_king = board.get_all_moves('white')

    # Kiểm tra nếu vua đen bị chiếu
    if board.is_in_check('black') and black_king_pos:
        r, c = black_king_pos
        rect = pygame.Rect(c * square, r * square, square, square)
        # Vẽ viền đỏ cho ô vua đen bị chiếu
        pygame.draw.rect(screen, (255, 0, 0), rect, 5)
        check_king = board.get_all_moves('black')


def display_game_result(winner):
    # Màu nền mờ
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Hiển thị kết quả (ai thắng)
    font_large = pygame.font.Font(None, 150)
    if winner == 'white':
        result_text = font_large.render("WHITE WINS!", True, (255, 255, 255))
    else:
        result_text = font_large.render("BLACK WINS!", True, (255, 255, 0))

    # Thêm bóng đổ
    shadow_text = font_large.render(
        winner.upper() + " WINS!", True, (50, 50, 50))
    screen.blit(shadow_text, ((WIDTH-160) // 2 - shadow_text.get_width() // 2 + 3,
                              HEIGHT // 3 - shadow_text.get_height() // 2 + 3))
    screen.blit(result_text, ((WIDTH-160) // 2 - result_text.get_width() // 2,
                              HEIGHT // 3 - result_text.get_height() // 2))

    # Nút Continue và Quit
    continue_rect = pygame.Rect(
        (WIDTH - 160) // 2 - 100, HEIGHT // 2 + 50, 200, 50)
    quit_rect = pygame.Rect((WIDTH - 160) // 2 - 100,
                            HEIGHT // 2 + 120, 200, 50)

    pygame.draw.rect(screen, (50, 205, 50), continue_rect)  # Xanh lá
    pygame.draw.rect(screen, (255, 69, 0), quit_rect)  # Đỏ cam

    font_small = pygame.font.Font(None, 50)
    continue_text = font_small.render("Continue", True, (255, 255, 255))
    quit_text = font_small.render("Quit", True, (255, 255, 255))

    screen.blit(continue_text, ((WIDTH-160) // 2 - continue_text.get_width() // 2,
                                HEIGHT // 2 + 60))
    screen.blit(quit_text, ((WIDTH-160) // 2 - quit_text.get_width() // 2,
                            HEIGHT // 2 + 130))


def display_choose_color_screen():
    # Màn hình chọn màu
    screen.fill((173, 216, 230))  # Nền hồng cho màn hình chọn màu

    # Hiển thị thông báo yêu cầu người chơi chọn phe
    choose_text = font_1.render("Choose Your Color", True, (255, 255, 255))
    screen.blit(choose_text, (WIDTH // 2 - choose_text.get_width() //
                2, HEIGHT // 3 - choose_text.get_height() // 2))

    # Vẽ nút "White"
    white_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    # Nút "White" màu trắng
    pygame.draw.rect(screen, (255, 255, 255), white_rect)
    white_text = font.render("White", True, (255, 182, 193))
    screen.blit(white_text, (WIDTH // 2 -
                white_text.get_width() // 2, HEIGHT // 2 + 10))

    # Vẽ nút "Black"
    black_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255),
                     black_rect)  # Nút "Black" màu đen
    black_text = font.render("Black", True, (255, 182, 193))
    screen.blit(black_text, (WIDTH // 2 -
                black_text.get_width() // 2, HEIGHT // 2 + 80))

    pygame.display.flip()
# Vẽ màn hình chọn mức độ


def display_choose_difficulty_screen():
    screen.fill((173, 216, 230))  # Nền hồng cho màn hình chọn mức độ

    choose_text = font_1.render(
        "Choose Your Difficulty", True, (255, 255, 255))
    screen.blit(choose_text, (WIDTH // 2 - choose_text.get_width() //
                2, HEIGHT // 3 - choose_text.get_height() // 2))

    easy_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), easy_rect)
    easy_text = font.render("Easy", True, (255, 182, 193))
    screen.blit(easy_text, (WIDTH // 2 -
                easy_text.get_width() // 2, HEIGHT // 2 + 10))

    medium_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), medium_rect)
    medium_text = font.render("Medium", True, (255, 182, 193))
    screen.blit(medium_text, (WIDTH // 2 -
                medium_text.get_width() // 2, HEIGHT // 2 + 80))

    hard_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), hard_rect)
    hard_text = font.render("Hard", True, (255, 182, 193))
    screen.blit(hard_text, (WIDTH // 2 -
                hard_text.get_width() // 2, HEIGHT // 2 + 150))

    pygame.display.flip()
# Lấy mức độ từ màn hình


def get_difficulty():
    difficulty = None
    while difficulty is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                if pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50).collidepoint(x, y):
                    difficulty = 'easy'
                elif pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50).collidepoint(x, y):
                    difficulty = 'medium'
                elif pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 50).collidepoint(x, y):
                    difficulty = 'hard'

    return difficulty

# Màn hình chọn loại đối thủ (Minimax / Random / AI vs AI)


def display_choose_opponent_screen():
    screen.fill((173, 216, 230))
    choose_text = font_1.render("Choose Opponent", True, (255, 255, 255))
    screen.blit(choose_text, (WIDTH // 2 - choose_text.get_width() //
                2, HEIGHT // 3 - choose_text.get_height() // 2))

    mini_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), mini_rect)
    mini_text = font.render("Minimax", True, (255, 182, 193))
    screen.blit(mini_text, (WIDTH // 2 -
                mini_text.get_width() // 2, HEIGHT // 2 + 10))

    rand_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), rand_rect)
    rand_text = font.render("Random", True, (255, 182, 193))
    screen.blit(rand_text, (WIDTH // 2 -
                rand_text.get_width() // 2, HEIGHT // 2 + 80))

    ai_vs_ai_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), ai_vs_ai_rect)
    ai_vs_ai_text = font.render("AI vs AI", True, (255, 182, 193))
    screen.blit(ai_vs_ai_text, (WIDTH // 2 -
                ai_vs_ai_text.get_width() // 2, HEIGHT // 2 + 150))

    human_vs_human_rect = pygame.Rect(
        WIDTH // 2 - 100, HEIGHT // 2 + 210, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), human_vs_human_rect)
    human_vs_human_text = font.render("Human vs Human", True, (255, 182, 193))
    screen.blit(human_vs_human_text, (WIDTH // 2 -
                human_vs_human_text.get_width() // 2, HEIGHT // 2 + 220))

    pygame.display.flip()


def get_opponent():
    opponent = None
    while opponent is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50).collidepoint(x, y):
                    opponent = 'minimax'
                elif pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50).collidepoint(x, y):
                    opponent = 'random'
                elif pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 50).collidepoint(x, y):
                    opponent = 'ai_vs_ai'
                elif pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 210, 200, 50).collidepoint(x, y):
                    opponent = 'human_vs_human'
    return opponent


def display_ai_vs_ai_config():
    screen.fill((173, 216, 230))
    choose_text = font_1.render("AI vs AI Config", True, (255, 255, 255))
    screen.blit(choose_text, (WIDTH // 2 - choose_text.get_width() //
                2, HEIGHT // 3 - choose_text.get_height() // 2))

    r_vs_m_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), r_vs_m_rect)
    r_vs_m_text = font.render("Random vs Minimax", True, (255, 182, 193))
    screen.blit(r_vs_m_text, (WIDTH // 2 -
                r_vs_m_text.get_width() // 2, HEIGHT // 2 + 10))

    m_vs_r_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), m_vs_r_rect)
    m_vs_r_text = font.render("Minimax vs Random", True, (255, 182, 193))
    screen.blit(m_vs_r_text, (WIDTH // 2 -
                m_vs_r_text.get_width() // 2, HEIGHT // 2 + 80))

    r_vs_r_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), r_vs_r_rect)
    r_vs_r_text = font.render("Random vs Random", True, (255, 182, 193))
    screen.blit(r_vs_r_text, (WIDTH // 2 -
                r_vs_r_text.get_width() // 2, HEIGHT // 2 + 150))

    m_vs_m_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 210, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), m_vs_m_rect)
    m_vs_m_text = font.render("Minimax vs Minimax", True, (255, 182, 193))
    screen.blit(m_vs_m_text, (WIDTH // 2 -
                m_vs_m_text.get_width() // 2, HEIGHT // 2 + 220))

    pygame.display.flip()


def get_ai_vs_ai_config():
    cfg = None
    while cfg is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50).collidepoint(x, y):
                    cfg = ('random', 'minimax')
                elif pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50).collidepoint(x, y):
                    cfg = ('minimax', 'random')
                elif pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 50).collidepoint(x, y):
                    cfg = ('random', 'random')
                elif pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 210, 200, 50).collidepoint(x, y):
                    cfg = ('minimax', 'minimax')
    return cfg


def random_agent_move(board, color):
    moves = board.get_all_moves(color)
    if not moves:
        return None
    return random.choice(moves)


def display_controller_screen(color_name):
    screen.fill((173, 216, 230))
    title = font_1.render(
        f"Select {color_name} Controller", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

    human_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), human_rect)
    human_text = font.render("Human", True, (255, 182, 193))
    screen.blit(human_text, (WIDTH // 2 -
                human_text.get_width() // 2, HEIGHT // 2 - 20))

    mini_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), mini_rect)
    mini_text = font.render("Minimax", True, (255, 182, 193))
    screen.blit(mini_text, (WIDTH // 2 -
                mini_text.get_width() // 2, HEIGHT // 2 + 50))

    rand_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 110, 200, 50)
    pygame.draw.rect(screen, (255, 255, 255), rand_rect)
    rand_text = font.render("Random", True, (255, 182, 193))
    screen.blit(rand_text, (WIDTH // 2 -
                rand_text.get_width() // 2, HEIGHT // 2 + 120))

    pygame.display.flip()


def get_controller_for(color_name):
    choice = None
    while choice is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 50).collidepoint(x, y):
                    choice = 'human'
                elif pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 50).collidepoint(x, y):
                    choice = 'minimax'
                elif pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 110, 200, 50).collidepoint(x, y):
                    choice = 'random'
        # render screen while waiting
        display_controller_screen(color_name)
    return choice


difficulty = None
board = Board()
game_over = False
game_started = False
white_controller = None
black_controller = None
start_time = None
elapsed_time = 0
last_loser = None  # Lưu bên thua để xác định người thắng
while running:
    if difficulty is None:
        display_choose_difficulty_screen()
        difficulty = get_difficulty()

    # Tiếp tục với phần code trò chơi (chọn màu cờ và chơi)
    if difficulty == 'easy':
        board.evaluate = board.evaluate
    elif difficulty == 'medium':
        board.evaluate = board.evaluate_1
    elif difficulty == 'hard':
        board.evaluate = board.evaluate_2
    # Single mode: Random agent (White) vs Minimax AI (Black)
    # Bỏ lựa chọn controller — luôn tự động bắt đầu trận Random vs Minimax
    white_controller = 'random'
    black_controller = 'minimax'
    if not game_started:
        game_started = True
        start_time = pygame.time.get_ticks()
        turn = 'white'

    if game_started:

        # Kiểm tra thời gian đã trôi qua
        if not game_over:
            elapsed_time = pygame.time.get_ticks() - start_time
            if elapsed_time >= time_limit:
                print("Hết thời gian! Trò chơi kết thúc.")
                game_over = True

        # Xử lý lượt: xác định controller của bên đang đi
        current_controller = white_controller if turn == 'white' else black_controller

        # Nếu bên đang đi là human, xử lý sự kiện click để di chuyển
        if current_controller == 'human':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and game_over == False:
                    x, y = pygame.mouse.get_pos()
                    if x < WIDTH - 160:
                        row, col = y//((WIDTH - 160)//8), x//(HEIGHT//8)
                        if selected:
                            # Nếu đã chọn quân, và click vào ô trong nước đi hợp lệ -> di chuyển
                            if (row, col) in valid_moves:
                                board.move_piece((selected, (row, col)))
                                turn = 'black' if turn == 'white' else 'white'
                                move_sound.play()
                            selected = None
                            valid_moves = []
                        else:
                            # Chọn quân của mình
                            p = board.board[row][col]
                            if p and p.color == turn:
                                selected = (row, col)
                                moves = board.get_all_moves(turn)
                                valid_moves = [
                                    dest for (src, dest) in moves if src == selected]
        else:
            # Lượt AI: chọn hành vi theo controller (minimax/random)
            move = None
            if current_controller == 'minimax':
                score, move = minimax(
                    board, 3, -math.inf, math.inf, turn == 'white')
            elif current_controller == 'random':
                move = random_agent_move(board, turn)

            if move:
                board.move_piece(move)
                # Nếu cả hai bên là AI thì thêm chút pause để dễ quan sát
                if white_controller in ('random', 'minimax') and black_controller in ('random', 'minimax'):
                    pygame.time.wait(200)
                turn = 'black' if turn == 'white' else 'white'
            else:
                # Kiểm tra xem bên hiện tại có bị chiếu không
                if board.is_in_check(turn):
                    print(f"{turn} is in check and has no legal moves. Game over.")
                    last_loser = turn
                else:
                    print(f"{turn} has no legal moves. Stalemate.")
                    last_loser = None
                game_over = True

        # Vẽ khu vực tính điểm và thời gian
        screen.fill((0, 0, 0))  # Đặt màu nền cho màn hình là đen

        # Vẽ khu vực bàn cờ (bên trái màn hình)
        board_rect = pygame.Rect(0, 0, WIDTH - 160, HEIGHT)
        # Nền trắng cho bàn cờ
        pygame.draw.rect(screen, (255, 255, 255), board_rect)
        draw_board()  # Vẽ bàn cờ trong khu vực này

        # Vẽ khu vực hiển thị thời gian và điểm số (bên phải màn hình)
        info_rect = pygame.Rect(WIDTH - 160, 0, 200, HEIGHT)
        # Nền xám cho khu vực hiển thị
        pygame.draw.rect(screen, (50, 50, 50), info_rect)

        # Hiển thị thời gian đã trôi qua (Tính bằng phút:giây)
        elapsed_minutes = elapsed_time // 60000  # Tính phút
        elapsed_seconds = (elapsed_time % 60000) // 1000  # Tính giây
        time_text_1 = "Elapsed:"  # Dòng 1
        time_text_2 = f"{elapsed_minutes:02}:{elapsed_seconds:02}"  # Dòng 2

        # Hiển thị giới hạn thời gian (Tính bằng phút:giây)
        limit_minutes = time_limit // 60000  # Tính phút
        limit_seconds = (time_limit % 60000) // 1000  # Tính giây
        limit_text_1 = "Time Limit:"  # Dòng 1
        limit_text_2 = f"{limit_minutes:02}:{limit_seconds:02}"  # Dòng 2

        # Hiển thị thời gian đã trôi qua
        time_surface_1 = font.render(time_text_1, True, (255, 255, 255))
        time_surface_2 = font.render(time_text_2, True, (255, 255, 255))
        screen.blit(time_surface_1, (WIDTH - 150, 20))  # Dòng 1
        screen.blit(time_surface_2, (WIDTH - 150, 50))  # Dòng 2

        # Hiển thị giới hạn thời gian
        limit_surface_1 = font.render(limit_text_1, True, (255, 255, 255))
        limit_surface_2 = font.render(limit_text_2, True, (255, 255, 255))
        screen.blit(limit_surface_1, (WIDTH - 150, 90))  # Dòng 1
        screen.blit(limit_surface_2, (WIDTH - 150, 120))  # Dòng 2

        if game_over:
            # Xác định người thắng và hiển thị kết quả
            continue_rect = pygame.Rect(
                (WIDTH - 160) // 2 - 100, HEIGHT // 2 + 50, 200, 50)
            quit_rect = pygame.Rect(
                (WIDTH - 160) // 2 - 100, HEIGHT // 2 + 120, 200, 50)

            # Xác định người thắng (người không thua)
            if last_loser == 'white':
                winner = 'black'
            elif last_loser == 'black':
                winner = 'white'
            else:
                winner = None  # Hòa

            display_game_result(winner if winner else 'draw')

            # Kiểm tra sự kiện nhấp chuột
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_buttons = pygame.mouse.get_pressed()

            # Continue: chơi ván mới
            if mouse_buttons[0] == 1 and continue_rect.collidepoint(mouse_x, mouse_y):
                board = Board()
                game_over = False
                game_started = False
                white_controller = None
                black_controller = None
                start_time = None
                last_loser = None
                turn = 'white'

            # Quit
            elif mouse_buttons[0] == 1 and quit_rect.collidepoint(mouse_x, mouse_y):
                running = False

        pygame.display.flip()
        pygame.time.Clock().tick(60)
