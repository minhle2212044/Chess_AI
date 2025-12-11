import pygame
import sys
import math
import random
import copy

from Gameplay.board import Board
from Gameplay.move import Pawn, Knight, Bishop, Rook, Queen, King
from Minimax.minimax import minimax
from ML.evaluate import AIPlayer
from ML.adapter import to_chess_board, from_uci_move
import chess
# -----------------------
# Pygame init & constants
# -----------------------
ml_agent = AIPlayer(
    model_path="ML/models/TORCH_100EPOCHS.pth",
    map_path="ML/models/move_to_int"
)
pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass

WIDTH = 980
HEIGHT = 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Artificial Intelligence - Chess Engine Project")

# Fonts & Colors
FONT = pygame.font.SysFont(None, 24)
FONT_MED = pygame.font.SysFont(None, 30)
FONT_LARGE = pygame.font.SysFont(None, 48)
FONT_TITLE = pygame.font.SysFont(None, 20)

BG = (18, 18, 20)
PANEL_BG = (30, 30, 34)
WHITE_SQ = (232, 232, 232)
BLACK_SQ = (139, 69, 19)
TEXT_COLOR = (245, 245, 245)
CHECK_BORDER = (255, 60, 60)

SQUARE = 80
BOARD_W = 8 * SQUARE
BOARD_H = 8 * SQUARE
SIDEBAR_W = WIDTH - BOARD_W

# Menu options
TIME_OPTIONS = [0, 5, 10, 15]  # minutes; 0 = unlimited
MODE_OPTIONS = [
    "Human vs Minimax",
    "Human vs ML",
    "Random vs Minimax",
    "Random vs ML"
]

selected_time = 0
selected_mode = MODE_OPTIONS[0]

fps_clock = pygame.time.Clock()

# -----------------------
# Helper functions
# -----------------------
def format_clock(ms):
    if ms is None:
        return "∞"
    if ms < 0:
        ms = 0
    mm = ms // 60000
    ss = (ms % 60000) // 1000
    return f"{mm:02}:{ss:02}"

def draw_center_text(surface, text, font, color, rect):
    surf = font.render(text, True, color)
    surface.blit(surf, (rect.x + (rect.w - surf.get_width())//2, rect.y + (rect.h - surf.get_height())//2))

# -----------------------
# Menu rendering
# -----------------------
def render_menu():
    screen.fill(BG)
    title_surf = FONT_LARGE.render("Artificial Intelligence - Chess Engine Project", True, TEXT_COLOR)
    screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 40))

    panel_w, panel_h = 520, 360
    panel_x = WIDTH//2 - panel_w//2
    panel_y = 120
    panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
    pygame.draw.rect(screen, PANEL_BG, panel, border_radius=10)
    pygame.draw.rect(screen, (80,80,90), panel, 2, border_radius=10)

    # Time box
    time_rect = pygame.Rect(panel_x + 40, panel_y + 30, panel_w - 80, 64)
    pygame.draw.rect(screen, (55,55,60), time_rect, border_radius=6)
    draw_center_text(screen,
                     f"Time: {'Unlimited' if selected_time==0 else f'{selected_time} min'}",
                     FONT_MED, TEXT_COLOR, time_rect)

    # Mode box
    mode_rect = pygame.Rect(panel_x + 40, panel_y + 110, panel_w - 80, 64)
    pygame.draw.rect(screen, (55,55,60), mode_rect, border_radius=6)
    draw_center_text(screen,
                     f"Mode: {selected_mode}",
                     FONT_MED, TEXT_COLOR, mode_rect)

    # Play button
    play_rect = pygame.Rect(panel_x + 110, panel_y + 200, panel_w - 220, 64)
    pygame.draw.rect(screen, (10,130,200), play_rect, border_radius=8)
    draw_center_text(screen, "PLAY GAME", FONT_MED, (255,255,255), play_rect)

    # Quit
    quit_rect = pygame.Rect(panel_x + 110, panel_y + 280, panel_w - 220, 40)
    pygame.draw.rect(screen, (70,70,70), quit_rect, border_radius=8)
    draw_center_text(screen, "QUIT", FONT, (255,255,255), quit_rect)

    pygame.display.flip()
    return time_rect, mode_rect, play_rect, quit_rect

def menu_loop():
    global selected_time, selected_mode
    while True:
        time_r, mode_r, play_r, quit_r = render_menu()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx,my = ev.pos
                if time_r.collidepoint(mx,my):
                    idx = TIME_OPTIONS.index(selected_time)
                    selected_time = TIME_OPTIONS[(idx+1) % len(TIME_OPTIONS)]
                elif mode_r.collidepoint(mx,my):
                    idx = MODE_OPTIONS.index(selected_mode)
                    selected_mode = MODE_OPTIONS[(idx+1) % len(MODE_OPTIONS)]
                elif play_r.collidepoint(mx,my):
                    return
                elif quit_r.collidepoint(mx,my):
                    pygame.quit(); sys.exit()
        fps_clock.tick(30)

# -----------------------
# Popup result
# -----------------------
def show_result_popup(winner_text, reason_text, moves_done):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(230)
    overlay.fill((10,10,10))
    screen.blit(overlay, (0,0))

    box = pygame.Rect(WIDTH//2 - 320, HEIGHT//2 - 160, 640, 320)
    pygame.draw.rect(screen, (40,40,45), box, border_radius=10)
    pygame.draw.rect(screen, (120,120,130), box, 2, border_radius=10)

    draw_center_text(screen, winner_text, FONT_LARGE, (255,255,255), pygame.Rect(box.x, box.y+20, box.w, 60))
    draw_center_text(screen, reason_text, FONT_MED, (230,230,230), pygame.Rect(box.x, box.y+90, box.w, 40))
    draw_center_text(screen, f"Moves: {moves_done}", FONT_MED, (200,200,200), pygame.Rect(box.x, box.y+140, box.w, 40))

    ok_btn = pygame.Rect(box.x + (box.w - 160)//2, box.y + 210, 160, 48)
    pygame.draw.rect(screen, (10,130,200), ok_btn, border_radius=8)
    draw_center_text(screen, "OK", FONT, (255,255,255), ok_btn)

    pygame.display.flip()

    # WAIT UNTIL USER PRESSES OK
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ok_btn.collidepoint(ev.pos):
                return

# -----------------------
# Board drawing & UI
# -----------------------
def draw_board(board, selected_sq, valid_moves):
    for r in range(8):
        for c in range(8):
            rect = pygame.Rect(c*SQUARE, r*SQUARE, SQUARE, SQUARE)
            color = WHITE_SQ if (r+c)%2==0 else BLACK_SQ
            pygame.draw.rect(screen, color, rect)

    # highlight selected
    if selected_sq:
        sr, sc = selected_sq
        pygame.draw.rect(screen, (255,240,150), (sc*SQUARE, sr*SQUARE, SQUARE, SQUARE), 4)

    # highlight valid moves
    for (mr, mc) in valid_moves:
        pygame.draw.rect(screen, (100,180,255), (mc*SQUARE, mr*SQUARE, SQUARE, SQUARE), 4)

    # draw pieces
    for r in range(8):
        for c in range(8):
            p = board.board[r][c]
            if p:
                cls_name = p.__class__.__name__.lower()
                path = f"../Assets/{p.color}_{cls_name}.png"
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.smoothscale(img, (SQUARE, SQUARE))
                    screen.blit(img, (c*SQUARE, r*SQUARE))
                except Exception:
                    # fallback
                    pygame.draw.circle(screen, (200,200,200), (c*SQUARE + SQUARE//2, r*SQUARE + SQUARE//2), 26)
                    ch = FONT.render(cls_name[0].upper(), True, (10,10,10))
                    screen.blit(ch, (c*SQUARE + SQUARE//2 - ch.get_width()//2, r*SQUARE + SQUARE//2 - ch.get_height()//2))

# -----------------------
# Move notation helpers (basic SAN-ish)
# -----------------------
def to_san(board, move, color, is_capture=False, is_promotion=False, promotion_piece='Q'):
    """
    Convert move tuple ((r1,c1),(r2,c2)) to SAN-like string:
    - Castling handled
    - Pawn: e4 or exd5
    - Pieces: Nf3, Rxe5
    - Promotion: e8=Q
    - Suffixes + or # are added externally if known
    This is a simplified SAN (does not do full disambiguation).
    """
    (r1,c1), (r2,c2) = move
    piece = board.board[r1][c1]

    # castling
    if isinstance(piece, King) and abs(c2 - c1) == 2:
        if c2 == 6:
            return "O-O"
        else:
            return "O-O-O"

    dst = f"{chr(c2 + 97)}{8 - r2}"
    if isinstance(piece, Pawn):
        if is_capture:
            return f"{chr(c1 + 97)}x{dst}"
        else:
            if is_promotion:
                return f"{dst}={promotion_piece}"
            return dst

    # piece letter
    letter = ""
    if isinstance(piece, Knight): letter = "N"
    elif isinstance(piece, Bishop): letter = "B"
    elif isinstance(piece, Rook): letter = "R"
    elif isinstance(piece, Queen): letter = "Q"
    elif isinstance(piece, King): letter = "K"

    if is_capture:
        return f"{letter}x{dst}"
    else:
        return f"{letter}{dst}"

# -----------------------
# Sidebar drawing with 2-column move list and notification
# -----------------------
def draw_sidebar(white_time_display, black_time_display, move_count, mode_name, move_pairs, notification):
    # background
    pygame.draw.rect(screen, PANEL_BG, (BOARD_W, 0, SIDEBAR_W, HEIGHT))

    # header
    screen.blit(FONT_TITLE.render("Game Panel", True, (220,220,220)), (BOARD_W + 14, 14))
    screen.blit(FONT.render(f"Mode: {mode_name}", True, (220,220,220)), (BOARD_W + 14, 44))
    screen.blit(FONT.render(f"Moves: {move_count}", True, (220,220,220)), (BOARD_W + 14, 74))

    # clocks (style A)
    screen.blit(FONT_MED.render("WHITE", True, (255,255,255)), (BOARD_W + 14, 110))
    screen.blit(FONT_MED.render(format_clock(white_time_display), True, (255,255,255)), (BOARD_W + 150, 110))
    screen.blit(FONT_MED.render("BLACK", True, (255,255,255)), (BOARD_W + 14, 150))
    screen.blit(FONT_MED.render(format_clock(black_time_display), True, (255,255,255)), (BOARD_W + 150, 150))

    # Move list box
    hist_rect = pygame.Rect(BOARD_W + 14, 200, SIDEBAR_W - 28, 300)
    pygame.draw.rect(screen, (40,40,46), hist_rect, border_radius=6)
    pygame.draw.rect(screen, (90,90,100), hist_rect, 2, border_radius=6)

    # header row for moves
    header = FONT.render("No.   White         Black", True, (220,220,220))
    screen.blit(header, (hist_rect.x + 8, hist_rect.y + 6))

    # display last N rows (two-column)
    rows_to_show = 12
    start_index = max(0, len(move_pairs) - rows_to_show)
    y = hist_rect.y + 32
    for i, pair in enumerate(move_pairs[start_index:], start=start_index+1):
        wmove, bmove = pair if isinstance(pair, tuple) else (pair, "")
        w_disp = wmove if wmove is not None else ""
        b_disp = bmove if bmove is not None else ""
        text = FONT.render(f"{i:>2}.   {w_disp:<12} {b_disp}", True, (235,235,235))
        screen.blit(text, (hist_rect.x + 8, y))
        y += 22

    # notification box (for Human vs AI)
    note_rect = pygame.Rect(BOARD_W + 14, HEIGHT - 170, SIDEBAR_W - 28, 56)
    pygame.draw.rect(screen, (50,50,60), note_rect, border_radius=6)
    pygame.draw.rect(screen, (100,100,110), note_rect, 2, border_radius=6)
    note_txt = FONT.render(notification, True, (235,235,235))
    screen.blit(note_txt, (note_rect.x + 10, note_rect.y + 18))

    # Buttons
    restart_btn = pygame.Rect(BOARD_W + 14, HEIGHT - 100, SIDEBAR_W - 28, 36)
    menu_btn = pygame.Rect(BOARD_W + 14, HEIGHT - 52, SIDEBAR_W - 28, 36)
    pygame.draw.rect(screen, (10,130,200), restart_btn, border_radius=6)
    draw_center_text(screen, "Restart Match", FONT, (255,255,255), restart_btn)
    pygame.draw.rect(screen, (70,70,70), menu_btn, border_radius=6)
    draw_center_text(screen, "Back to Menu", FONT, (255,255,255), menu_btn)

    return restart_btn, menu_btn

# -----------------------
# Agents
# -----------------------
def random_agent_move(board, color):
    moves = board.get_all_moves(color)
    return random.choice(moves) if moves else None

def ml_agent_move(board, color):
    cb = to_chess_board(board, color)
    mv = ml_agent.get_move(cb)
    return from_uci_move(mv.uci())

# -----------------------
# Time utilities
# -----------------------
def remaining_display(side, white_ms, black_ms, turn, turn_start):
    now = pygame.time.get_ticks()
    elapsed = now - turn_start
    if side == "white":
        return None if white_ms is None else max(0, white_ms - (elapsed if turn == "white" else 0))
    else:
        return None if black_ms is None else max(0, black_ms - (elapsed if turn == "black" else 0))

def deduct_clock(side, elapsed, white_ms, black_ms):
    if side == "white" and white_ms is not None:
        white_ms = max(0, white_ms - elapsed)
    if side == "black" and black_ms is not None:
        black_ms = max(0, black_ms - elapsed)
    return white_ms, black_ms

# -----------------------
# Convert move to PGN-ish (full SAN is complex; we implement practical)
# -----------------------
def move_to_san_full(board, move, color):
    """
    Build SAN-like notation with:
    - piece letters KQRBN
    - captures (x)
    - promotion (=Q)
    - castling O-O / O-O-O
    - check (+) and mate (#) will be appended by caller if detected
    Note: This function is simplified, doesn't fully disambiguate ambiguous piece moves.
    """
    (r1,c1), (r2,c2) = move
    piece = board.board[r1][c1]
    # detect capture
    target = board.board[r2][c2]
    is_capture = target is not None

    # castling
    if isinstance(piece, King) and abs(c2 - c1) == 2:
        return "O-O" if c2 == 6 else "O-O-O"

    # Pawn moves
    dst = f"{chr(c2 + 97)}{8 - r2}"
    if isinstance(piece, Pawn):
        # en-passant detect requires additional state; not implemented here
        if is_capture:
            return f"{chr(c1 + 97)}x{dst}"
        # promotion
        if r2 in (0,7):
            return f"{dst}=Q"
        return dst

    # piece letter
    letter = ""
    if isinstance(piece, Knight): letter = "N"
    elif isinstance(piece, Bishop): letter = "B"
    elif isinstance(piece, Rook): letter = "R"
    elif isinstance(piece, Queen): letter = "Q"
    elif isinstance(piece, King): letter = "K"

    if is_capture:
        return f"{letter}x{dst}"
    return f"{letter}{dst}"

# -----------------------
# Main match loop
# -----------------------
def run_match():
    board = Board()
    turn = "white"
    move_count = 0
    move_pairs = []
    pending_white = None
    notification = "Game started"

    # clock setup
    if selected_time == 0:
        white_ms = None
        black_ms = None
    else:
        white_ms = selected_time * 60000
        black_ms = selected_time * 60000

    turn_start = pygame.time.get_ticks()
    game_over = False

    # determine controllers
    if selected_mode == "Human vs Minimax":
        controllers = {"white": "human", "black": "minimax"}
    elif selected_mode == "Human vs ML":
        controllers = {"white": "human", "black": "ml"}
    elif selected_mode == "Random vs Minimax":
        controllers = {"white": "random", "black": "minimax"}
    elif selected_mode == "Random vs ML":
        controllers = {"white": "random", "black": "ml"}
    else:
        controllers = {"white": "human", "black": "human"}

    selected_sq = None
    valid_moves = []

    while True:
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        now = pygame.time.get_ticks()
        elapsed = now - turn_start

        # update clocks
        w_disp = remaining_display("white", white_ms, black_ms, turn, turn_start)
        b_disp = remaining_display("black", white_ms, black_ms, turn, turn_start)

        # TIMEOUT CHECK
        if not game_over:
            if w_disp is not None and w_disp <= 0:
                show_result_popup("Black wins", "White ran out of time", move_count)
                game_over = True
            if b_disp is not None and b_disp <= 0:
                show_result_popup("White wins", "Black ran out of time", move_count)
                game_over = True

        # ------------------------------
        # IF GAME OVER → FREEZE BOARD
        # ------------------------------
        if game_over:
            screen.fill(BG)

            # Show board
            draw_board(board, None, [])

            # Move history (2 columns)
            move_pairs_display = list(move_pairs)
            if pending_white:
                move_pairs_display.append((pending_white, ""))

            # Draw sidebar
            restart_btn, menu_btn = draw_sidebar(
                w_disp, b_disp, move_count, selected_mode,
                move_pairs_display, notification
            )

            # Allow clicking menu & restart ONLY
            for ev in events:
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = ev.pos
                    if restart_btn.collidepoint(mx, my):
                        return  # restart game
                    if menu_btn.collidepoint(mx, my):
                        return  # back to menu

            pygame.display.flip()
            continue  # skip rest of loop

        # ------------------------------
        # NOT GAME OVER → PROCESS TURNS
        # ------------------------------

        controller = controllers[turn]

        # ---- HUMAN TURN ----
        if controller == "human":
            notification = "Your turn"

            for ev in events:
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = ev.pos

                    # sidebar buttons check
                    restart_btn, menu_btn = draw_sidebar(
                        w_disp, b_disp, move_count, selected_mode,
                        move_pairs, notification
                    )

                    if restart_btn.collidepoint(mx, my):
                        return
                    if menu_btn.collidepoint(mx, my):
                        return

                    if mx < BOARD_W and my < BOARD_H:
                        r = my // SQUARE
                        c = mx // SQUARE

                        if selected_sq:
                            # try move
                            if (r, c) in valid_moves:
                                white_ms, black_ms = deduct_clock(turn, elapsed, white_ms, black_ms)

                                mv = (selected_sq, (r, c))
                                san = move_to_san_full(board, mv, turn)
                                board.move_piece(mv)
                                move_count += 1

                                # record SAN
                                pending_white = san

                                # switch turn
                                turn = "black"
                                turn_start = pygame.time.get_ticks()

                                selected_sq = None
                                valid_moves = []
                            else:
                                # choose another piece
                                p = board.board[r][c]
                                if p and p.color == turn:
                                    selected_sq = (r, c)
                                    moves = board.get_all_moves(turn)
                                    valid_moves = [d for (s, d) in moves if s == selected_sq]
                                else:
                                    selected_sq = None
                                    valid_moves = []
                        else:
                            p = board.board[r][c]
                            if p and p.color == turn:
                                selected_sq = (r, c)
                                moves = board.get_all_moves(turn)
                                valid_moves = [d for (s, d) in moves if s == selected_sq]

        # ---- AI TURN (Minimax / Random / ML) ----
        else:
            if controller == "ml":
                notification = "ML is thinking..."
            elif controller == "minimax":
                notification = "Minimax is thinking..."
            else:
                notification = "Random AI is thinking..."

            # compute AI time
            ai_start = pygame.time.get_ticks()

            if controller == "random":
                mv = random_agent_move(board, turn)

            elif controller == "minimax":
                _, mv = minimax(board, 3, -math.inf, math.inf, turn == "white")

            elif controller == "ml":
                mv = ml_agent_move(board, turn)  # ML agent

            ai_end = pygame.time.get_ticks()
            ai_elapsed = ai_end - ai_start

            white_ms, black_ms = deduct_clock(turn, ai_elapsed, white_ms, black_ms)

            if mv:
                san = move_to_san_full(board, mv, turn)

                board.move_piece(mv)
                move_count += 1

                if turn == "white":
                    pending_white = san
                else:
                    move_pairs.append((pending_white, san))
                    pending_white = None

                # update notification
                if controller == "ml":
                    notification = f"ML played: {san}"
                elif controller == "minimax":
                    notification = f"Minimax played: {san}"
                else:
                    notification = f"Random played: {san}"

                # switch turn
                turn = "black" if turn == "white" else "white"
                turn_start = pygame.time.get_ticks()

            else:
                # no moves → checkmate or stalemate
                if board.is_in_check(turn):
                    winner = "Black" if turn == "white" else "White"
                    show_result_popup(f"{winner} wins", "Checkmate", move_count)
                else:
                    show_result_popup("Draw", "Stalemate", move_count)

                game_over = True
                continue

        # ----- DRAW UI -----
        screen.fill(BG)
        draw_board(board, selected_sq, valid_moves)

        move_pairs_display = list(move_pairs)
        if pending_white:
            move_pairs_display.append((pending_white, ""))

        restart_btn, menu_btn = draw_sidebar(
            w_disp, b_disp, move_count, selected_mode,
            move_pairs_display, notification
        )

        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos
                if restart_btn.collidepoint(mx, my):
                    return
                if menu_btn.collidepoint(mx, my):
                    return

        pygame.display.flip()
        fps_clock.tick(60)

# -----------------------
# Entry point
# -----------------------
def main():
    while True:
        menu_loop()
        run_match()

if __name__ == "__main__":
    main()
