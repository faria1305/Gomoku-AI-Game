import tkinter as tk
import math

BOARD_SIZE = 10
WINNING_COUNT = 5
WINNING_SCORE = 999999999
go_board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
player = -1  
winner = 0

root = tk.Tk()
root.title("Gomoku Game")

# Create a main frame to hold the board and side panel
main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack()

# Create a board frame
board_frame = tk.Frame(main_frame, bg="#D2B48C", bd=5, relief="solid")  # Adding border and background color
board_frame.grid(row=0, column=0, padx=10)

# Create a side panel for options and status
side_panel = tk.Frame(main_frame, bg="#f0f0f0", bd=5, relief="solid")  # Light gray background and border
side_panel.grid(row=0, column=1, padx=10, sticky="n")

# Center the content in the side panel
side_panel.grid_rowconfigure(0, weight=1)
side_panel.grid_rowconfigure(4, weight=1)

# Styled labels for "You (Black)" and "AI (White)"
player_label = tk.Label(side_panel, text="You (⚫ Black)", font=("Arial", 14), bg="black", fg="white", width=15, relief="solid", padx=5, pady=5)
player_label.grid(row=1, column=0, pady=5, padx=10)

ai_label = tk.Label(side_panel, text="AI (⚪ White)", font=("Arial", 14), bg="white", fg="black", width=15, relief="solid", padx=5, pady=5)
ai_label.grid(row=2, column=0, pady=5, padx=10)

# Status label for game status updates with blue background
status_label = tk.Label(side_panel, text="Your turn!", font=("Arial", 14), bg="#2196F3", fg="white", width=15, relief="solid", padx=5, pady=5)
status_label.grid(row=3, column=0, pady=10, padx=10)

# New Game button in the side panel
def reset_game():
    global go_board, player, winner
    go_board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    player = -1  
    winner = 0
    status_label.config(text="Your turn!", bg="#2196F3")
    update_board_ui()
    enable_all_buttons()

new_game_button = tk.Button(side_panel, text="New Game", font=("Arial", 12), command=reset_game, bg="#4CAF50", fg="white", width=10)
new_game_button.grid(row=4, column=0, pady=20, padx=10)

# Button setup with board color
buttons = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def print_board(board):
    for i in range(len(board)):
        print(board[i])

def update_board_ui():
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            buttons[i][j].config(text=" ", state="normal", bg="#D2B48C")  # Reset button appearance
            if go_board[i][j] == -1:
                buttons[i][j].config(text="⚫", state="disabled", fg="black")  # Dark black stone for player
            elif go_board[i][j] == 1:
                buttons[i][j].config(text="⚪", state="disabled", fg="white")  # Bright white stone for AI

def move(row, col, player):
    if go_board[row][col] == 0 and player in (-1, 1):
        go_board[row][col] = player
        update_board_ui()
        return True
    return False

def check_win(board, player):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == player:
                if j <= BOARD_SIZE - WINNING_COUNT and all(board[i][j + k] == player for k in range(WINNING_COUNT)):
                    return True
                if i <= BOARD_SIZE - WINNING_COUNT and all(board[i + k][j] == player for k in range(WINNING_COUNT)):
                    return True
                if i <= BOARD_SIZE - WINNING_COUNT and j <= BOARD_SIZE - WINNING_COUNT and all(board[i + k][j + k] == player for k in range(WINNING_COUNT)):
                    return True
                if i <= BOARD_SIZE - WINNING_COUNT and j >= WINNING_COUNT - 1 and all(board[i + k][j - k] == player for k in range(WINNING_COUNT)):
                    return True
    return False

def check_sequence(board, row, col, player, length, direction):
    """Check for sequences of pieces in a given direction"""
    count = 0
    open_ends = 0
    dx, dy = direction
    
    # Check backward
    r, c = row - dx, col - dy
    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == 0:
        open_ends += 1
        
    # Count consecutive pieces
    r, c = row, col
    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and count < length:
        if board[r][c] != player:
            break
        count += 1
        r, c = r + dx, c + dy
        
    # Check forward
    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == 0:
        open_ends += 1
        
    return count == length and open_ends > 0

def find_winning_move(board, player):
    """Find a winning move for the player"""
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == 0:
                board[i][j] = player
                if check_win(board, player):
                    board[i][j] = 0
                    return (i, j)
                board[i][j] = 0
    return None

def find_four_threat(board, player):
    """Find a move that blocks opponent's four-in-a-row"""
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == 0:
                for dx, dy in directions:
                    # Check for four consecutive pieces
                    count = 0
                    r, c = i, j
                    while (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and 
                           count < 4 and board[r][c] == player):
                        count += 1
                        r, c = r + dx, c + dy
                    if count == 4:
                        return (i, j)
    return None

def find_open_three(board, player):
    """Find a move that creates or blocks an open three"""
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == 0:
                for dx, dy in directions:
                    if check_sequence(board, i, j, player, 3, (dx, dy)):
                        return (i, j)
    return None

def get_candidate_moves(board):
    """Get a list of candidate moves near existing pieces"""
    moves = set()
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] != 0:
                # Add adjacent empty cells
                for di in range(-1, 2):
                    for dj in range(-1, 2):
                        ni, nj = i + di, j + dj
                        if (0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE and 
                            board[ni][nj] == 0):
                            moves.add((ni, nj))
    return list(moves) if moves else [(BOARD_SIZE // 2, BOARD_SIZE // 2)]

def evaluate_position(board, player):
    """Evaluate the current board position"""
    score = 0
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == player:
                # Check all directions for patterns
                for dx, dy in directions:
                    # Count consecutive pieces and open ends
                    count = 0
                    open_ends = 0
                    r, c = i, j
                    
                    while (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and 
                           board[r][c] == player and count < 5):
                        count += 1
                        r, c = r + dx, c + dy
                    
                    # Check ends
                    if (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and 
                        board[r][c] == 0):
                        open_ends += 1
                    r, c = i - dx, j - dy
                    if (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and 
                        board[r][c] == 0):
                        open_ends += 1
                        
                    # Score based on length and openness
                    if count == 4:
                        score += 1000 if open_ends > 0 else 100
                    elif count == 3:
                        score += 100 if open_ends == 2 else 10
                    elif count == 2:
                        score += 10 if open_ends == 2 else 1
                        
    return score

def min_max_alpha_beta(board, depth, alpha, beta, player):
    if depth == 0:
        return evaluate_position(board, 1) - evaluate_position(board, -1)
    
    moves = get_candidate_moves(board)
    if not moves:
        return 0
        
    if player == 1:
        max_eval = float(-math.inf)
        for i, j in moves:
            if board[i][j] == 0:
                board[i][j] = 1
                eval = min_max_alpha_beta(board, depth - 1, alpha, beta, -1)
                board[i][j] = 0
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = float(math.inf)
        for i, j in moves:
            if board[i][j] == 0:
                board[i][j] = -1
                eval = min_max_alpha_beta(board, depth - 1, alpha, beta, 1)
                board[i][j] = 0
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval

def best_move(board, player):
    # Priority 1: Win if possible
    winning_move = find_winning_move(board, player)
    if winning_move:
        return winning_move
        
    # Priority 2: Block opponent's win
    opponent = -player
    blocking_move = find_winning_move(board, opponent)
    if blocking_move:
        return blocking_move
        
    # Priority 3: Block opponent's closed four
    four_block = find_four_threat(board, opponent)
    if four_block:
        return four_block
        
    # Priority 4: Create/block open three
    three_move = find_open_three(board, player)
    if three_move:
        return three_move
        
    # Priority 5: Use minimax for other moves
    moves = get_candidate_moves(board)
    best_score = float(-math.inf)
    best_pos = moves[0]
    
    for row, col in moves:
        if board[row][col] == 0:
            board[row][col] = player
            score = min_max_alpha_beta(board, 3, -math.inf, math.inf, -player)
            board[row][col] = 0
            if score > best_score:
                best_score = score
                best_pos = (row, col)
                
    return best_pos

def is_board_full(go_board):
    return all(cell != 0 for row in go_board for cell in row)



# Additional game logic functions (check_win, AI logic, etc.) remain unchanged

def on_cell_click(row, col):
    global player, winner
    if move(row, col, player):
        if check_win(go_board, player):
            winner = player
            status_label.config(text="You win!", fg="white", bg="#4CAF50")
            disable_all_buttons()
        else:
            player = 1
            status_label.config(text="AI's turn", bg="#2196F3", fg="white")
            root.after(500, ai_move)

def ai_move():
    global player, winner
    if winner == 0 and not is_board_full(go_board):
        row, col = best_move(go_board, player)
        move(row, col, player)
        if check_win(go_board, player):
            winner = player
            status_label.config(text="AI wins!", fg="white", bg="red")
            disable_all_buttons()
        else:
            player = -1
            status_label.config(text="Your turn", fg="white", bg="#2196F3")

def disable_all_buttons():
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            buttons[i][j].config(state="disabled")

def enable_all_buttons():
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            buttons[i][j].config(state="normal")

# Create the game board buttons with a board color
for i in range(BOARD_SIZE):
    for j in range(BOARD_SIZE):
        button = tk.Button(board_frame, width=4, height=2, font=("Arial", 14), bg="#D2B48C",
                           command=lambda i=i, j=j: on_cell_click(i, j))  # Light tan color
        button.grid(row=i, column=j)  # Start at row=2 to make room for labels and status
        buttons[i][j] = button

root.mainloop()