import random


# =============================================================
#  SUDOKU AS A CONSTRAINT SATISFACTION PROBLEM (CSP)
#
#  Variables  : every empty cell on the 9x9 board
#  Domain     : {1, 2, 3, 4, 5, 6, 7, 8, 9}
#  Constraints: no duplicate in same row, column, or 3x3 box
#  Goal       : complete assignment where no constraint is violated
#
#  Enhancements used (from AI-1 CSP lecture):
#    1. MRV  - Minimum Remaining Values  (which cell to fill next)
#    2. FC   - Forward Checking          (detect dead ends early)
# =============================================================


# -------------------------------------------------------------
#  CONSTRAINT CHECK
# -------------------------------------------------------------

def is_valid(board, row, col, num):
    """
    Returns True if placing 'num' at board[row][col] violates
    no Sudoku constraint (row / column / 3x3 box).
    This is the core CONSTRAINT function of the CSP.
    """

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


# -------------------------------------------------------------
#  DOMAIN FUNCTION
# -------------------------------------------------------------

def get_domain(board, row, col):
    """
    Returns the list of numbers that can legally go in board[row][col].
    This is the DOMAIN of the variable (cell) in CSP terms.
    """
    return [n for n in range(1, 10) if is_valid(board, row, col, n)]


# -------------------------------------------------------------
#  ENHANCEMENT 1: MRV (Minimum Remaining Values)
#  Pick the empty cell with the fewest valid numbers left.
#  Lecture slides 23-26.
# -------------------------------------------------------------

def select_mrv_cell(board):
    """
    Scans every empty cell and returns (row, col) of the one
    whose domain is smallest — the most constrained cell.
    Returns None if the board is full (no empty cells).
    """
    best_row, best_col = -1, -1
    best_count = 10          # higher than max possible (9)

    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                count = len(get_domain(board, row, col))

                if count == 0:
                    return (row, col)    # dead end found immediately

                if count < best_count:
                    best_count = count
                    best_row, best_col = row, col

    if best_row == -1:
        return None                      # board is complete

    return (best_row, best_col)


# -------------------------------------------------------------
#  ENHANCEMENT 2: FORWARD CHECKING (FC)
#  After placing a number, check if any neighbor is now stuck.
#  Lecture slides 38-46.
# -------------------------------------------------------------

def forward_check(board, row, col):
    """
    After placing a value at board[row][col], checks all empty
    cells in the same row, column, and 3x3 box.
    Returns False immediately if any neighbor has an empty domain.
    """
    related = set()

    for i in range(9):
        related.add((row, i))
        related.add((i, col))

    box_row = (row // 3) * 3
    box_col = (col // 3) * 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            related.add((r, c))

    for (r, c) in related:
        if board[r][c] == 0:
            if len(get_domain(board, r, c)) == 0:
                return False    # neighbor has no valid values left

    return True


# -------------------------------------------------------------
#  ENHANCED SOLVER: Backtracking + MRV + Forward Checking
# -------------------------------------------------------------

def solve(board):
    """
    Solves the board using backtracking with MRV and Forward Checking.

    Steps:
      1. MRV: pick the most constrained empty cell
      2. Get its domain (valid numbers)
      3. Try each number
      4. Forward Check: if a neighbor is now stuck, backtrack
      5. Recurse on the rest of the board
      6. If nothing works, undo and return False (backtrack)
      7. If no empty cells remain, return True (solved)

    Modifies board in place.
    """

    # Step 1: MRV — which cell to fill?
    cell = select_mrv_cell(board)

    if cell is None:
        return True             # no empty cells → solved!

    row, col = cell

    # Step 2: domain of this cell
    domain = get_domain(board, row, col)

    if not domain:
        return False            # dead end

    # Step 3 & 4: try each number with forward checking
    for num in domain:
        board[row][col] = num

        if forward_check(board, row, col):
            if solve(board):
                return True

        board[row][col] = 0     # backtrack

    return False


# -------------------------------------------------------------
#  BOARD GENERATOR
# -------------------------------------------------------------

def generate_full_board():
    """Generates a completely filled valid Sudoku board."""
    board = [[0] * 9 for _ in range(9)]

    def fill(board):
        cell = select_mrv_cell(board)
        if cell is None:
            return True

        row, col = cell
        nums = list(range(1, 10))
        random.shuffle(nums)

        for num in nums:
            if is_valid(board, row, col, num):
                board[row][col] = num
                if fill(board):
                    return True
                board[row][col] = 0

        return False

    fill(board)
    return board


# -------------------------------------------------------------
#  UNIQUE SOLUTION CHECKER
# -------------------------------------------------------------

def count_solutions(board, limit=2):
    """
    Counts solutions up to 'limit'.
    Used to guarantee the puzzle has exactly one solution.
    """
    count = [0]

    def _solve(board):
        if count[0] >= limit:
            return
        cell = select_mrv_cell(board)
        if cell is None:
            count[0] += 1
            return
        row, col = cell
        for num in range(1, 10):
            if is_valid(board, row, col, num):
                board[row][col] = num
                _solve(board)
                board[row][col] = 0

    board_copy = [row[:] for row in board]
    _solve(board_copy)
    return count[0]


# -------------------------------------------------------------
#  PUZZLE CREATOR
# -------------------------------------------------------------

def remove_numbers(board, num_to_remove=50):
    """
    Removes cells from a full board to create a puzzle.
    After each removal, verifies exactly one solution remains.
    Default 50 removals = 31 clues left (challenging puzzle).
    """
    puzzle = [row[:] for row in board]
    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)

    removed = 0
    for row, col in positions:
        if removed >= num_to_remove:
            break

        backup = puzzle[row][col]
        puzzle[row][col] = 0

        if count_solutions(puzzle) == 1:
            removed += 1
        else:
            puzzle[row][col] = backup

    return puzzle


def new_game():
    """Returns (puzzle, solution) — both 9x9 lists."""
    full_board = generate_full_board()
    solution   = [row[:] for row in full_board]
    puzzle     = remove_numbers(full_board, num_to_remove=50)
    return puzzle, solution


# -------------------------------------------------------------
#  SOLUTION VALIDATOR
# -------------------------------------------------------------

def check_solution(board):
    """Returns True if board is a complete valid Sudoku solution."""
    full_set = set(range(1, 10))

    for row in range(9):
        if set(board[row]) != full_set:
            return False

    for col in range(9):
        if set(board[r][col] for r in range(9)) != full_set:
            return False

    for br in range(3):
        for bc in range(3):
            box = {board[br*3+r][bc*3+c] for r in range(3) for c in range(3)}
            if box != full_set:
                return False

    return True


# -------------------------------------------------------------
#  QUICK TEST
# -------------------------------------------------------------

if __name__ == "__main__":
    import time

    print("Generating puzzle (MRV + Forward Checking)...\n")
    t0 = time.time()
    puzzle, solution = new_game()
    t1 = time.time()

    clues = sum(1 for r in range(9) for c in range(9) if puzzle[r][c] != 0)
    print(f"Generated in {t1-t0:.2f}s  |  Clues: {clues}/81\n")

    for row in puzzle:
        print(row)

    print("\nSolving...")
    t2 = time.time()
    copy = [row[:] for row in puzzle]
    solve(copy)
    t3 = time.time()

    print(f"Solved in {t3-t2:.4f}s  |  Valid: {check_solution(copy)}")
