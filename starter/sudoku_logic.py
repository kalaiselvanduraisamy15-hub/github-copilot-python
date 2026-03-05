import copy
import random

SIZE = 9
EMPTY = 0


def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def find_empty_with_fewest_candidates(board):
    best_cell = None
    best_candidates = None

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != EMPTY:
                continue
            candidates = [num for num in range(1, SIZE + 1) if is_safe(board, row, col, num)]
            if not candidates:
                return (row, col), []
            if best_candidates is None or len(candidates) < len(best_candidates):
                best_cell = (row, col)
                best_candidates = candidates
                if len(best_candidates) == 1:
                    return best_cell, best_candidates

    return best_cell, best_candidates


def count_solutions(board, limit=2):
    count = 0

    def backtrack():
        nonlocal count
        if count >= limit:
            return

        cell, candidates = find_empty_with_fewest_candidates(board)
        if cell is None:
            count += 1
            return
        if not candidates:
            return

        row, col = cell
        random.shuffle(candidates)
        for candidate in candidates:
            board[row][col] = candidate
            backtrack()
            board[row][col] = EMPTY
            if count >= limit:
                return

    backtrack()
    return count


def remove_cells_with_uniqueness(board, clues):
    target_removals = SIZE * SIZE - clues
    if target_removals <= 0:
        return True

    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)

    removed = 0
    for row, col in cells:
        if removed >= target_removals:
            break
        if board[row][col] == EMPTY:
            continue

        saved = board[row][col]
        board[row][col] = EMPTY

        if count_solutions(deep_copy(board), limit=2) != 1:
            board[row][col] = saved
        else:
            removed += 1

    return removed == target_removals

def generate_puzzle(clues=35):
    clues = max(17, min(clues, SIZE * SIZE))

    for _ in range(50):
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)

        puzzle = deep_copy(board)
        if remove_cells_with_uniqueness(puzzle, clues):
            return puzzle, solution

    raise RuntimeError("Could not generate a uniquely solvable puzzle with requested clues")
