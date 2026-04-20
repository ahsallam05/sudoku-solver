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
    """Solve the board using backtracking. Modifies board in place."""
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


def count_solutions(board, limit=2):
    """
    Counts how many solutions a board has, up to 'limit'.

    We only need to know if there's exactly 1 solution.
    Stopping at 2 keeps it fast — we don't need to count all of them.

    Returns 0, 1, or 2 (meaning "2 or more").
    """
    count = [0]   # using a list so the nested function can modify it

    def _solve(board):
        if count[0] >= limit:
            return  # already found enough, stop searching

        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if is_valid(board, row, col, num):
                            board[row][col] = num
                            _solve(board)
                            board[row][col] = 0  # backtrack
                    return  # no valid number -> dead end, return

        count[0] += 1  # reached here = board is full = found a solution

    board_copy = [row[:] for row in board]
    _solve(board_copy)
    return count[0]


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


def remove_numbers(board, difficulty="medium"):
    """
    Remove numbers from a full board to create a puzzle.

    KEY FIX: After removing each number, we check that the puzzle
    still has exactly one solution. If removing a number creates
    multiple solutions, we put it back and try elsewhere.

    difficulty:
      "easy"   -> remove 30 numbers
      "medium" -> remove 40 numbers
      "hard"   -> remove 50 numbers
    """

    remove_counts = {
        "easy":   30,
        "medium": 40,
        "hard":   50,
    }
    target = remove_counts.get(difficulty, 40)

    puzzle = [row[:] for row in board]

    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)

    removed = 0
    for row, col in positions:
        if removed >= target:
            break

        backup = puzzle[row][col]
        puzzle[row][col] = 0

        if count_solutions(puzzle) == 1:
            removed += 1
        else:
            puzzle[row][col] = backup  # put it back

    return puzzle


def new_game(difficulty="medium"):
    """Generate a new puzzle and its solution."""
    full_board = generate_full_board()
    solution = [row[:] for row in full_board]
    puzzle = remove_numbers(full_board, difficulty)
    return puzzle, solution


def check_solution(board):
    """Check if the board is fully and correctly solved."""
    for row in range(9):
        if set(board[row]) != set(range(1, 10)):
            return False

    for col in range(9):
        column = [board[row][col] for row in range(9)]
        if set(column) != set(range(1, 10)):
            return False

    for box_row in range(3):
        for box_col in range(3):
            box = []
            for r in range(3):
                for c in range(3):
                    box.append(board[box_row * 3 + r][box_col * 3 + c])
            if set(box) != set(range(1, 10)):
                return False

    return True


if __name__ == "__main__":
    print("Generating puzzle...")
    puzzle, solution = new_game("medium")

    print("\nPuzzle (0 = empty):")
    for row in puzzle:
        print(row)

    # IMPORTANT: solve a COPY, never the original puzzle
    puzzle_copy = [row[:] for row in puzzle]
    solve(puzzle_copy)

    print("\nSolved copy valid?", check_solution(puzzle_copy))
