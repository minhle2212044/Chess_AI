import chess
import torch
import numpy as np
import pickle
import random
from tqdm import tqdm

from ML.engines.auxiliary_func import board_to_matrix
from ML.engines.model import ChessModel

MODEL_PATH = "models/TORCH_100EPOCHS.pth" 
MAP_PATH = "models/move_to_int"
LOG_FILE = "game_history.txt"

class AIPlayer:
    def __init__(self, model_path, map_path, device=None):
        self.device = device if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"AI Agent đang chạy trên: {self.device}")

        # Load Mapping
        try:
            with open(map_path, "rb") as file:
                self.move_to_int = pickle.load(file)
                self.int_to_move = {v: k for k, v in self.move_to_int.items()}
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file mapping tại {map_path}")
            exit()

        # Load Model
        self.model = ChessModel(num_classes=len(self.move_to_int))
        try:
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        except FileNotFoundError:
             print(f"Lỗi: Không tìm thấy file model tại {model_path}")
             exit()
             
        self.model.to(self.device)
        self.model.eval()

    def get_move(self, board: chess.Board):
        matrix = board_to_matrix(board)
        X_tensor = torch.tensor(matrix, dtype=torch.float32).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(X_tensor)
        
        logits = logits.squeeze(0)
        probabilities = torch.softmax(logits, dim=0).cpu().numpy()
        
        legal_moves = list(board.legal_moves)
        legal_moves_uci = [move.uci() for move in legal_moves]

        sorted_indices = np.argsort(probabilities)[::-1]

        for move_index in sorted_indices:
            move_uci = self.int_to_move.get(move_index)
            if move_uci in legal_moves_uci:
                return chess.Move.from_uci(move_uci)
        
        # Fallback
        print(f"\n[CẢNH BÁO] AI Fallback: Model bí nước! Sử dụng Random move tại lượt {board.fullmove_number} (Bên {'Trắng' if board.turn else 'Đen'})")
        return random.choice(legal_moves)
    
    def get_probabilities(self, board):
        matrix = board_to_matrix(board)
        X_tensor = torch.tensor(matrix, dtype=torch.float32).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(X_tensor)

        probs = torch.softmax(logits.squeeze(0), dim=0).cpu().numpy()
        return probs

def get_random_move(board: chess.Board):
    """Chọn một nước đi ngẫu nhiên từ các nước đi hợp lệ."""
    legal_moves = list(board.legal_moves)
    return random.choice(legal_moves)

def play_game(player_white, player_black):
    """
    Mô phỏng 1 ván đấu.
    Trả về: 1 (Trắng thắng), -1 (Đen thắng), 0 (Hòa)
    """
    board = chess.Board()

    max_moves = 200 
    move_count = 0

    while not board.is_game_over() and move_count < max_moves:
        if board.turn == chess.WHITE:
            move = player_white(board)
        else:
            move = player_black(board)
        
        board.push(move)
        move_count += 1

    result = board.result()
    
    score = 0
    if result == "1-0":
        score = 1
    elif result == "0-1":
        score = -1
    else:
        score = 0
    
    return score, board

def log_game_to_file(file_path, game_index, white_name, black_name, board):
    """Hàm ghi thông tin ván đấu vào file txt"""
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"--- Game #{game_index} ---\n")
        f.write(f"White: {white_name} | Black: {black_name}\n")
        f.write(f"Result: {board.result()} (Moves: {board.fullmove_number})\n")
        
        # Ghi danh sách các nước đi (UCI format: e2e4, e7e5...)
        moves = [move.uci() for move in board.move_stack]
        f.write(f"Moves: {' '.join(moves)}\n")
        f.write("\n")
        

def main():
    ai_agent = AIPlayer(MODEL_PATH, MAP_PATH)
    
    num_games = 100
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"KẾT QUẢ THI ĐẤU (Total: {num_games*2} games)\n")
        f.write("============================================\n\n")

    print(f"\nBắt đầu thi đấu {num_games} ván giữa AI (Trắng) và Random (Đen)...")
    
    ai_wins = 0
    random_wins = 0
    draws = 0

    # AI cầm quân Trắng, Random cầm quân Đen
    for i in tqdm(range(num_games)):
        score, final_board = play_game(ai_agent.get_move, get_random_move)
        
        # Ghi log
        log_game_to_file(LOG_FILE, i+1, "AI", "Random", final_board)

        if score == 1:
            ai_wins += 1
        elif score == -1:
            random_wins += 1
        else:
            draws += 1

    print("\n--- KẾT QUẢ CUỐI CÙNG (AI cầm Trắng) ---")
    print(f"AI Thắng     : {ai_wins} ({ai_wins/num_games*100:.1f}%)")
    print(f"Random Thắng : {random_wins} ({random_wins/num_games*100:.1f}%)")
    print(f"Hòa          : {draws} ({draws/num_games*100:.1f}%)")

    # Đổi bên: Random cầm Trắng, AI cầm Đen
    # print(f"\nBắt đầu thi đấu {num_games} ván giữa Random (Trắng) và AI (Đen)...")
    # ai_wins = 0
    # random_wins = 0
    # draws = 0
    
    # for i in tqdm(range(num_games)):
    #     score, final_board = play_game(get_random_move, ai_agent.get_move)
        

    #     log_game_to_file(LOG_FILE, num_games + i + 1, "Random", "AI", final_board)

    #     if score == 1:
    #         random_wins += 1
    #     elif score == -1:
    #         ai_wins += 1
    #     else:
    #         draws += 1
            
    # print("\n--- KẾT QUẢ CUỐI CÙNG (AI cầm Đen) ---")
    # print(f"AI Thắng     : {ai_wins} ({ai_wins/num_games*100:.1f}%)")
    # print(f"Random Thắng : {random_wins} ({random_wins/num_games*100:.1f}%)")
    # print(f"Hòa          : {draws} ({draws/num_games*100:.1f}%)")
    # print(f"\nChi tiết các trận đấu đã được lưu tại: {LOG_FILE}")

if __name__ == "__main__":
    main()