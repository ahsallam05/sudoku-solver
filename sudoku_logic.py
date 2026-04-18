import random


def is_valid(board, row, col, num):
    """Check if placing num at board[row][col] is valid."""
    if num in board[row]:
        return False

    for r in range(9):
        if board[r][col] == num:
            return False

    box_row = (row // 3) * 3
    box_col = (col // 3) * 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if board[r][c] == num:
                return False

    return True


def solve(board):
    """Solve the board using backtracking."""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve(board):
                            return True
                        board[row][col] = 0
                return False
    return True


def generate_full_board():
    """Generate a complete valid Sudoku board."""
    board = [[0] * 9 for _ in range(9)]

    def fill(board):
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        if is_valid(board, row, col, num):
                            board[row][col] = num
                            if fill(board):
                                return True
                            board[row][col] = 0
                    return False
        return True

    fill(board)
    return board


def remove_numbers(board):
    """Remove 35 numbers to create an easy puzzle."""
    puzzle = [row[:] for row in board]
    removed = 0
    while removed < 35:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        if puzzle[row][col] != 0:
            puzzle[row][col] = 0
            removed += 1
    return puzzle


def new_game():
    """Generate a new puzzle and its solution."""
    full_board = generate_full_board()
    solution = [row[:] for row in full_board]
    puzzle = remove_numbers(full_board)
    return puzzle, solution


def check_solution(board):
    """Check if the board is fully solved correctly."""
    for row in range(9):
        if len(set(board[row])) != 9 or 0 in board[row]:
            return False

    for col in range(9):
        column = [board[row][col] for row in range(9)]
        if len(set(column)) != 9 or 0 in column:
            return False

    for box_row in range(3):
        for box_col in range(3):
            box = []
            for r in range(3):
                for c in range(3):
                    box.append(board[box_row * 3 + r][box_col * 3 + c])
            if len(set(box)) != 9 or 0 in box:
                return False

    return True


if __name__ == "__main__":
    puzzle, solution = new_game()
    print("Puzzle:")
    for row in puzzle:
        print(row)
    solve(puzzle)
    print("\nValid:", check_solution(puzzle))
