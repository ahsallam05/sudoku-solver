import tkinter as tk
from tkinter import messagebox
import time
from sudoku_logic import new_game, solve, check_solution


# =============================================================
#  COLOR PALETTE  — change values here to restyle the whole app
# =============================================================

BG_MAIN        = "#1e1e2e"   # main window background
BG_CELL        = "#2a2a3e"   # normal empty cell
BG_GIVEN       = "#12122a"   # pre-filled clue cell
BG_SELECTED    = "#e94560"   # currently selected cell (red)
BG_BOX_A       = "#2a2a3e"   # 3x3 box color A
BG_BOX_B       = "#22223a"   # 3x3 box color B (slight contrast)

FG_GIVEN       = "#ffffff"   # clue number color
FG_USER        = "#4fc3f7"   # user-typed number color (light blue)
FG_ERROR       = "#ff5252"   # wrong number color (red)
FG_SUCCESS     = "#69f0ae"   # correct/solved color (green)
FG_TITLE       = "#e94560"   # title color

BTN_SOLVE      = "#145a32"
BTN_CHECK      = "#1a5276"
BTN_RESET      = "#4a235a"
BTN_NEW        = "#e94560"

FONT_CELL      = ("Courier New", 18, "bold")
FONT_BUTTON    = ("Courier New", 11, "bold")
FONT_TITLE     = ("Courier New", 20, "bold")
FONT_SUBTITLE  = ("Courier New", 9)
FONT_TIMER     = ("Courier New", 13)
FONT_STATUS    = ("Courier New", 10)


# =============================================================
#  MAIN APPLICATION
# =============================================================

class SudokuApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku — CSP Solver")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)

        # ── game state ──
        self.puzzle    = None
        self.solution  = None
        self.given     = None         # True where cell is a clue
        self.sel_row   = -1
        self.sel_col   = -1

        # ── timer state ──
        self.start_time    = None
        self.elapsed_time  = 0
        self.timer_running = False

        # ── build UI ──
        self._build_title()
        self._build_grid()
        self._build_numpad()
        self._build_buttons()
        self._build_bottom_bar()

        # ── keyboard bindings ──
        self.root.bind("<Up>",        lambda e: self._move(-1,  0))
        self.root.bind("<Down>",      lambda e: self._move( 1,  0))
        self.root.bind("<Left>",      lambda e: self._move( 0, -1))
        self.root.bind("<Right>",     lambda e: self._move( 0,  1))
        self.root.bind("<Delete>",    lambda e: self._enter(0))
        self.root.bind("<BackSpace>", lambda e: self._enter(0))
        for i in range(1, 10):
            self.root.bind(str(i), lambda e, n=i: self._enter(n))

        # ── start first game ──
        self.new_game()


    # ----------------------------------------------------------
    #  UI BUILDERS
    # ----------------------------------------------------------

    def _build_title(self):
        frame = tk.Frame(self.root, bg=BG_MAIN, pady=8)
        frame.pack(fill="x")

        tk.Label(frame, text="◈  S U D O K U  ◈",
                 font=FONT_TITLE, bg=BG_MAIN, fg=FG_TITLE).pack()

        tk.Label(frame, text="CSP  ·  Backtracking  ·  MRV  ·  Forward Checking",
                 font=FONT_SUBTITLE, bg=BG_MAIN, fg="#666688").pack()


    def _build_grid(self):
        """
        Build the 9x9 grid.
        Each cell is a tk.Label stored in self.cells[row][col].
        Clicking a cell selects it; number keys fill it in.
        """
        # Red outer frame gives the thick border effect
        outer = tk.Frame(self.root, bg=FG_TITLE, padx=3, pady=3)
        outer.pack(pady=6)

        self.cells = [[None]*9 for _ in range(9)]

        for row in range(9):
            for col in range(9):

                # Alternate box colors so 3x3 boxes are visible
                box_index = (row // 3) * 3 + (col // 3)
                bg = BG_BOX_A if box_index % 2 == 0 else BG_BOX_B

                # Thicker padding on box boundaries creates visible separators
                pad_top  = 3 if row % 3 == 0 else 1
                pad_left = 3 if col % 3 == 0 else 1

                cell = tk.Label(
                    outer,
                    text="", width=2, height=1,
                    font=FONT_CELL, bg=bg, fg=FG_USER,
                    relief="flat", anchor="center",
                    padx=10, pady=8
                )
                cell.grid(
                    row=row, column=col,
                    padx=(pad_left, 1),
                    pady=(pad_top, 1),
                    sticky="nsew"
                )
                cell.bind("<Button-1>", lambda e, r=row, c=col: self._select(r, c))
                self.cells[row][col] = cell


    def _build_numpad(self):
        """Row of buttons 1–9 and a clear button."""
        frame = tk.Frame(self.root, bg=BG_MAIN, pady=4)
        frame.pack()

        for num in range(1, 10):
            btn = tk.Button(
                frame, text=str(num),
                width=3, height=1,
                font=FONT_BUTTON,
                bg="#0f3460", fg="#e0e0e0",
                relief="flat", cursor="hand2",
                command=lambda n=num: self._enter(n)
            )
            btn.pack(side="left", padx=2)
            self._hover(btn, "#0f3460")

        clear_btn = tk.Button(
            frame, text="✕",
            width=3, height=1,
            font=FONT_BUTTON,
            bg="#2a2a4e", fg=FG_ERROR,
            relief="flat", cursor="hand2",
            command=lambda: self._enter(0)
        )
        clear_btn.pack(side="left", padx=(10, 2))


    def _build_buttons(self):
        """Check / Solve / Reset action buttons."""
        frame = tk.Frame(self.root, bg=BG_MAIN, pady=6)
        frame.pack()

        for label, cmd, color in [
            ("✔  Check",  self.check,      BTN_CHECK),
            ("◉  Solve",  self.solve,      BTN_SOLVE),
            ("↺  Reset",  self.reset,      BTN_RESET),
            ("＋ New",    self.new_game,   BTN_NEW),
        ]:
            tk.Button(
                frame, text=label,
                font=FONT_BUTTON, bg=color, fg="white",
                relief="flat", padx=14, pady=5,
                cursor="hand2", command=cmd
            ).pack(side="left", padx=5)


    def _build_bottom_bar(self):
        """Timer on the left, status message on the right."""
        bar = tk.Frame(self.root, bg=BG_MAIN, pady=4)
        bar.pack(fill="x", padx=16)

        self.timer_label = tk.Label(
            bar, text="⏱  00:00",
            bg=BG_MAIN, fg="#aaaacc", font=FONT_TIMER
        )
        self.timer_label.pack(side="left")

        self.status_var = tk.StringVar(value="")
        tk.Label(
            bar, textvariable=self.status_var,
            bg=BG_MAIN, fg=FG_USER, font=FONT_STATUS
        ).pack(side="right")


    # ----------------------------------------------------------
    #  GAME LOGIC
    # ----------------------------------------------------------

    def new_game(self):
        """Start a fresh puzzle."""
        self.puzzle, self.solution = new_game()

        # Build a grid of True/False — True = pre-filled clue
        self.given = [
            [self.puzzle[r][c] != 0 for c in range(9)]
            for r in range(9)
        ]

        self.sel_row = self.sel_col = -1
        self._render()
        self._reset_timer()
        self._start_timer()

        clues = sum(1 for r in range(9) for c in range(9) if self.puzzle[r][c] != 0)
        self.status_var.set(f"New game  ·  {clues} clues")


    def _render(self):
        """Repaint all 81 cells from self.puzzle."""
        for r in range(9):
            for c in range(9):
                val       = self.puzzle[r][c]
                cell      = self.cells[r][c]
                box_index = (r // 3) * 3 + (c // 3)
                box_bg    = BG_BOX_A if box_index % 2 == 0 else BG_BOX_B

                if val == 0:
                    cell.config(text="", bg=box_bg, fg=FG_USER)
                elif self.given[r][c]:
                    cell.config(text=str(val), bg=BG_GIVEN, fg=FG_GIVEN)
                else:
                    cell.config(text=str(val), bg=box_bg, fg=FG_USER)


    def _select(self, row, col):
        """Highlight a cell when clicked. Clue cells cannot be selected."""
        if self.given[row][col]:
            return

        # Deselect previous cell
        if self.sel_row >= 0:
            pr, pc    = self.sel_row, self.sel_col
            box_index = (pr // 3) * 3 + (pc // 3)
            box_bg    = BG_BOX_A if box_index % 2 == 0 else BG_BOX_B
            self.cells[pr][pc].config(bg=box_bg)

        self.sel_row, self.sel_col = row, col
        self.cells[row][col].config(bg=BG_SELECTED)
        self.status_var.set(f"Row {row+1}  Col {col+1}")


    def _move(self, dr, dc):
        """Move selection with arrow keys, skipping given cells."""
        if self.sel_row < 0:
            self._select(0, 0)
            return

        r = max(0, min(8, self.sel_row + dr))
        c = max(0, min(8, self.sel_col + dc))

        # Skip over given cells in the direction of movement
        while 0 <= r <= 8 and 0 <= c <= 8 and self.given[r][c]:
            r = max(0, min(8, r + dr))
            c = max(0, min(8, c + dc))

        if 0 <= r <= 8 and 0 <= c <= 8:
            self._select(r, c)


    def _enter(self, num):
        """Place or clear a number in the selected cell."""
        if self.sel_row < 0:
            self.status_var.set("Click a cell first!")
            return

        r, c = self.sel_row, self.sel_col
        if self.given[r][c]:
            return

        self.puzzle[r][c] = num
        self.cells[r][c].config(
            text=str(num) if num else "",
            bg=BG_SELECTED,
            fg=FG_USER
        )


    def check(self):
        """
        Check the user's current board.
        - Wrong cells → red
        - Correct cells → blue
        - Fully solved → green + congratulations
        """
        errors = 0
        empty  = 0

        for r in range(9):
            for c in range(9):
                if self.given[r][c]:
                    continue

                val       = self.puzzle[r][c]
                box_index = (r // 3) * 3 + (c // 3)
                box_bg    = BG_BOX_A if box_index % 2 == 0 else BG_BOX_B

                if val == 0:
                    empty += 1
                elif val != self.solution[r][c]:
                    self.cells[r][c].config(fg=FG_ERROR)
                    errors += 1
                else:
                    self.cells[r][c].config(fg=FG_USER)

        if empty == 0 and errors == 0:
            self._stop_timer()
            elapsed = self._fmt(self.elapsed_time)
            for r in range(9):
                for c in range(9):
                    self.cells[r][c].config(fg=FG_SUCCESS)
            messagebox.showinfo("Solved! 🎉", f"Puzzle solved!\nTime: {elapsed}")
            self.status_var.set(f"Solved in {elapsed}! 🎉")
        elif empty > 0 and errors == 0:
            self.status_var.set(f"{empty} cells left — no errors so far!")
        else:
            self.status_var.set(f"{errors} error(s) found. Keep going!")


    def solve(self):
        """Auto-solve using the CSP backtracking solver."""
        board_copy = [row[:] for row in self.puzzle]

        if solve(board_copy):
            for r in range(9):
                for c in range(9):
                    self.puzzle[r][c] = board_copy[r][c]

            self._stop_timer()
            self._render()

            # Color solved cells green
            for r in range(9):
                for c in range(9):
                    if not self.given[r][c]:
                        self.cells[r][c].config(fg=FG_SUCCESS)

            self.status_var.set("Solved by CSP algorithm!")
        else:
            messagebox.showerror("Error", "No solution exists for this puzzle.")


    def reset(self):
        """Clear all user entries and restart the timer."""
        for r in range(9):
            for c in range(9):
                if not self.given[r][c]:
                    self.puzzle[r][c] = 0

        self.sel_row = self.sel_col = -1
        self._render()
        self._reset_timer()
        self._start_timer()
        self.status_var.set("Board reset.")


    # ----------------------------------------------------------
    #  TIMER
    # ----------------------------------------------------------

    def _start_timer(self):
        self.start_time    = time.time()
        self.timer_running = True
        self._tick()

    def _stop_timer(self):
        if self.timer_running:
            self.elapsed_time += time.time() - self.start_time
        self.timer_running = False

    def _reset_timer(self):
        self.timer_running = False
        self.elapsed_time  = 0
        self.start_time    = None
        self.timer_label.config(text="⏱  00:00")

    def _tick(self):
        if not self.timer_running:
            return
        total = self.elapsed_time + (time.time() - self.start_time)
        self.timer_label.config(text=f"⏱  {self._fmt(total)}")
        self.root.after(1000, self._tick)

    def _fmt(self, seconds):
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m:02d}:{s:02d}"


    # ----------------------------------------------------------
    #  HELPER
    # ----------------------------------------------------------

    def _hover(self, btn, original):
        """Button color changes on mouse hover."""
        btn.bind("<Enter>", lambda e: btn.config(bg=FG_TITLE, fg="white"))
        btn.bind("<Leave>", lambda e: btn.config(bg=original, fg="#e0e0e0"))
