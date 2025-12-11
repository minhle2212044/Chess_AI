import time
import os
import sys
import chess

try:
    from evaluate import AIPlayer, get_random_move, MODEL_PATH, MAP_PATH
except ImportError:
    print("Lỗi: Không tìm thấy file 'main.py' hoặc không thể import class AIPlayer.")
    sys.exit(1)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_board_fancy(board):
    print("\n  +-----------------+")
    
    board_str = board.unicode(invert_color=True)
    
    board_str = board_str.replace('⭘', '.') 

    rows = board_str.split("\n")
    
    for i, row in enumerate(rows):
        print(f"{8 - i} | {row} |")
        
    print("  +-----------------+")
    print("    a b c d e f g h\n")

def watch_match(ai_plays_white=True, delay=1.0):
    print("Đang khởi tạo AI...")
    ai_agent = AIPlayer(MODEL_PATH, MAP_PATH)
    
    board = chess.Board()

    if ai_plays_white:
        player_white = "AI"
        player_black = "Random Bot"
    else:
        player_white = "Random Bot"
        player_black = "AI"

    clear_screen()
    print(f"BẮT ĐẦU TRẬN ĐẤU: {player_white} (Trắng) vs {player_black} (Đen)")
    time.sleep(2)

    move_count = 0
    max_moves = 200

    while not board.is_game_over() and move_count < max_moves:
        clear_screen()
        
        print(f"Trận đấu: {player_white} vs {player_black}")
        print(f"Lượt đi thứ: {board.fullmove_number}")
        print(f"Bên đi: {'TRẮNG' if board.turn == chess.WHITE else 'ĐEN'}")
        
        print_board_fancy(board)
        
        if board.turn == chess.WHITE:
            if ai_plays_white:
                move = ai_agent.get_move(board)
                last_mover = "AI"
            else:
                move = get_random_move(board)
                last_mover = "Random"
        else: # Black turn
            if not ai_plays_white:
                move = ai_agent.get_move(board)
                last_mover = "AI"
            else:
                move = get_random_move(board)
                last_mover = "Random"

        print(f">>> {last_mover} đi: {move.uci()}")
        
        board.push(move)
        move_count += 1
        time.sleep(delay)

    # --- KẾT THÚC ---
    clear_screen()
    print("========== KẾT THÚC TRẬN ĐẤU ==========")
    print_board_fancy(board)
    print(f"Tổng số nước đi: {move_count}")
    print(f"Kết quả: {board.result()}")
    
    outcome = board.outcome()
    if outcome:
        winner = "Hòa"
        if outcome.winner == chess.WHITE:
            winner = player_white
        elif outcome.winner == chess.BLACK:
            winner = player_black
        
        print(f"Người thắng: {winner}")
        print(f"Lý do: {outcome.termination.name}")
    else:
        print("Trận đấu dừng do quá số lượt đi giới hạn.")

if __name__ == "__main__":
    print("Chọn chế độ xem:")
    print("1. AI cầm quân Trắng (Đi trước)")
    print("2. AI cầm quân Đen (Đi sau)")
    
    choice = input("Nhập lựa chọn (1 hoặc 2): ")
    
    try:
        speed = float(input("Nhập thời gian chờ mỗi nước đi (giây, vd: 0.5): "))
    except ValueError:
        speed = 1.0

    if choice == '2':
        watch_match(ai_plays_white=False, delay=speed)
    else:
        watch_match(ai_plays_white=True, delay=speed)