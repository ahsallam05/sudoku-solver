import tkinter as tk
from tkinter import messagebox
import time
from sudoku_logic import new_game, solve, check_solution


BG_MAIN        = "#1a1a2e"
BG_GRID        = "#16213e"
BG_BOX_LIGHT   = "#0f3460"
BG_BOX_DARK    = "#16213e"
BG_CELL_GIVEN  = "#0f3460"
BG_CELL_USER   = "#1a1a2e"
BG_CELL_SELECT = "#e94560"

FG_GIVEN       = "#e0e0e0"
FG_USER        = "#4fc3f7"
FG_ERROR       = "#ff5252"
FG_SUCCESS     = "#69f0ae"

BTN_BG         = "#0f3460"
BTN_FG         = "#e0e0e0"
BTN_HOVER      = "#e94560"

BORDER_THICK   = "#e94560"
BORDER_THIN    = "#2a2a4e"

FONT_NUMBERS   = ("Courier New", 18, "bold")
FONT_GIVEN     = ("Courier New", 18, "bold")
FONT_BUTTONS   = ("Courier New", 11, "bold")
FONT_TITLE     = ("Courier New", 22, "bold")
FONT_TIMER     = ("Courier New", 14)
FONT_STATUS    = ("Courier New", 11)


class SudokuApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)

        self.puzzle   = None
        self.solution = None
        self.given    = None
        self.selected_row = -1
        self.selected_col = -1

        self.start_time   = None
        self.elapsed_time = 0
        self.timer_running = False

        self._build_title()
        self._build_top_bar()
        self._build_grid()
        self._build_number_pad()
        self._build_buttons()
        self._build_status_bar()

        self.new_game()

        self.root.bind("<Up>",    lambda e: self._move_selection(-1, 0))
        self.root.bind("<Down>",  lambda e: self._move_selection(1, 0))
        self.root.bind("<Left>",  lambda e: self._move_selection(0, -1))
        self.root.bind("<Right>", lambda e: self._move_selection(0, 1))

        for i in range(1, 10):
            self.root.bind(str(i), lambda e, n=i: self._enter_number(n))
        self.root.bind("<Delete>",    lambda e: self._enter_number(0))
        self.root.bind("<BackSpace>", lambda e: self._enter_number(0))


    def _build_title(self):
        title_frame = tk.Frame(self.root, bg=BG_MAIN, pady=10)
        title_frame.pack(fill="x")
        tk.Label(
            title_frame,
            text="◈  S U D O K U  ◈",
            font=FONT_TITLE,
            bg=BG_MAIN,
            fg=BORDER_THICK
        ).pack()


    def _build_top_bar(self):
        bar = tk.Frame(self.root, bg=BG_MAIN, pady=5)
        bar.pack(fill="x", padx=20)

        self.timer_label = tk.Label(
            bar, text="⏱  00:00",
            bg=BG_MAIN, fg=FG_GIVEN, font=FONT_TIMER
        )
        self.timer_label.pack(side="left")

        new_btn = tk.Button(
            bar, text="New Game",
            bg=BORDER_THICK, fg="white", font=FONT_BUTTONS,
            relief="flat", padx=14, pady=4,
            cursor="hand2",
            command=self.new_game
        )
        new_btn.pack(side="right")


    def _build_grid(self):
        outer = tk.Frame(self.root, bg=BORDER_THICK, padx=3, pady=3)
        outer.pack(pady=10)
        self.cells = [[None for _ in range(9)] for _ in range(9)]

        for row in range(9):
            for col in range(9):
                box_index = (row // 3) * 3 + (col // 3)
                box_bg = BG_BOX_LIGHT if box_index % 2 == 0 else BG_BOX_DARK

                pad_top    = 3 if row % 3 == 0 else 1
                pad_left   = 3 if col % 3 == 0 else 1
                pad_bottom = 1
                pad_right  = 1

                cell = tk.Label(
                    outer,
                    text="",
                    width=2, height=1,
                    font=FONT_NUMBERS,
                    bg=box_bg,
                    fg=FG_USER,
                    relief="flat",
                    anchor="center",
                    padx=10, pady=8
                )
                cell.grid(
                    row=row, column=col,
                    padx=(pad_left, pad_right),
                    pady=(pad_top, pad_bottom),
                    sticky="nsew"
                )
                cell.bind("<Button-1>", lambda e, r=row, c=col: self._select_cell(r, c))
                self.cells[row][col] = cell


    def _build_number_pad(self):
        pad_frame = tk.Frame(self.root, bg=BG_MAIN, pady=5)
        pad_frame.pack()

        for num in range(1, 10):
            btn = tk.Button(
                pad_frame,
                text=str(num),
                width=3, height=1,
                font=FONT_BUTTONS,
                bg=BTN_BG, fg=BTN_FG,
                relief="flat",
                cursor="hand2",
                command=lambda n=num: self._enter_number(n)
            )
            btn.pack(side="left", padx=2)
            self._add_hover_effect(btn)

        clear_btn = tk.Button(
            pad_frame,
            text="✕",
            width=3, height=1,
            font=FONT_BUTTONS,
            bg="#2a2a4e", fg=FG_ERROR,
            relief="flat",
            cursor="hand2",
            command=lambda: self._enter_number(0)
        )
        clear_btn.pack(side="left", padx=(8, 2))


    def _build_buttons(self):
        btn_frame = tk.Frame(self.root, bg=BG_MAIN, pady=8)
        btn_frame.pack()

        buttons = [
            ("✔  Check",  self.check_solution,  "#1a5276"),
            ("◉  Solve",  self.solve_puzzle,    "#145a32"),
            ("↺  Reset",  self.reset_puzzle,    "#4a235a"),
        ]

        for label, command, color in buttons:
            btn = tk.Button(
                btn_frame,
                text=label,
                font=FONT_BUTTONS,
                bg=color, fg="white",
                relief="flat",
                padx=18, pady=6,
                cursor="hand2",
                command=command
            )
            btn.pack(side="left", padx=6)


    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="")
        status = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg=BG_MAIN,
            fg=FG_USER,
            font=FONT_STATUS,
            pady=6
        )
        status.pack()


    def new_game(self):
        self.puzzle, self.solution = new_game()
        self.given = [
            [self.puzzle[r][c] != 0 for c in range(9)]
            for r in range(9)
        ]
        self.selected_row = -1
        self.selected_col = -1
        self._render_board()
        self._reset_timer()
        self._start_timer()
        self.status_var.set("New game started. Good luck!")


    def _render_board(self):
        for row in range(9):
            for col in range(9):
                value = self.puzzle[row][col]
                cell  = self.cells[row][col]
                box_index = (row // 3) * 3 + (col // 3)
                box_bg = BG_BOX_LIGHT if box_index % 2 == 0 else BG_BOX_DARK

                if value == 0:
                    cell.config(text="", bg=box_bg, fg=FG_USER)
                elif self.given[row][col]:
                    cell.config(text=str(value), bg=BG_CELL_GIVEN, fg=FG_GIVEN)
                else:
                    cell.config(text=str(value), bg=box_bg, fg=FG_USER)


    def _select_cell(self, row, col):
        if self.given[row][col]:
            return

        if self.selected_row >= 0:
            prev_r = self.selected_row
            prev_c = self.selected_col
            box_index = (prev_r // 3) * 3 + (prev_c // 3)
            box_bg = BG_BOX_LIGHT if box_index % 2 == 0 else BG_BOX_DARK
            self.cells[prev_r][prev_c].config(bg=box_bg)

        self.selected_row = row
        self.selected_col = col
        self.cells[row][col].config(bg=BG_CELL_SELECT)
        self.status_var.set(f"Selected: row {row + 1}, col {col + 1}")


    def _move_selection(self, dr, dc):
        if self.selected_row < 0:
            self._select_cell(0, 0)
            return

        new_row = self.selected_row + dr
        new_col = self.selected_col + dc
        new_row = max(0, min(8, new_row))
        new_col = max(0, min(8, new_col))

        if self.given[new_row][new_col]:
            while 0 <= new_row <= 8 and 0 <= new_col <= 8:
                if not self.given[new_row][new_col]:
                    break
                new_row += dr
                new_col += dc
            else:
                return

        if 0 <= new_row <= 8 and 0 <= new_col <= 8:
            self._select_cell(new_row, new_col)


    def _enter_number(self, num):
        if self.selected_row < 0:
            self.status_var.set("Click a cell first!")
            return

        row = self.selected_row
        col = self.selected_col

        if self.given[row][col]:
            return

        self.puzzle[row][col] = num
        box_index = (row // 3) * 3 + (col // 3)
        box_bg = BG_BOX_LIGHT if box_index % 2 == 0 else BG_BOX_DARK

        if num == 0:
            self.cells[row][col].config(text="", bg=BG_CELL_SELECT, fg=FG_USER)
        else:
            self.cells[row][col].config(text=str(num), bg=BG_CELL_SELECT, fg=FG_USER)


    def check_solution(self):
        errors = 0
        empty  = 0

        for row in range(9):
            for col in range(9):
                cell  = self.cells[row][col]
                value = self.puzzle[row][col]
                box_index = (row // 3) * 3 + (col // 3)
                box_bg = BG_BOX_LIGHT if box_index % 2 == 0 else BG_BOX_DARK

                if self.given[row][col]:
                    continue

                if value == 0:
                    empty += 1
                elif value != self.solution[row][col]:
                    cell.config(fg=FG_ERROR)
                    errors += 1
                else:
                    cell.config(fg=FG_USER)

        if empty == 0 and errors == 0:
            self._stop_timer()
            elapsed = self._format_time(self.elapsed_time)
            for row in range(9):
                for col in range(9):
                    self.cells[row][col].config(fg=FG_SUCCESS)
            messagebox.showinfo(
                "Congratulations! 🎉",
                f"You solved the puzzle!\nTime: {elapsed}"
            )
            self.status_var.set(f"Solved in {elapsed}! 🎉")

        elif empty > 0 and errors == 0:
            self.status_var.set(f"{empty} cells remaining. Looking good so far!")

        else:
            self.status_var.set(f"{errors} error(s) found. Keep trying!")


    def solve_puzzle(self):
        board_copy = [row[:] for row in self.puzzle]

        if solve(board_copy):
            for r in range(9):
                for c in range(9):
                    self.puzzle[r][c] = board_copy[r][c]
            self._stop_timer()
            self._render_board()
            for r in range(9):
                for c in range(9):
                    if not self.given[r][c]:
                        self.cells[r][c].config(fg=FG_SUCCESS)
            self.status_var.set("Puzzle solved! Study the solution.")
        else:
            messagebox.showerror("Error", "This puzzle cannot be solved!")


    def reset_puzzle(self):
        for row in range(9):
            for col in range(9):
                if not self.given[row][col]:
                    self.puzzle[row][col] = 0

        self.selected_row = -1
        self.selected_col = -1
        self._render_board()
        self._reset_timer()
        self._start_timer()
        self.status_var.set("Board reset. Try again!")


    def _start_timer(self):
        self.start_time = time.time()
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
        self.timer_label.config(text=f"⏱  {self._format_time(total)}")
        self.root.after(1000, self._tick)


    def _format_time(self, seconds):
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{mins:02d}:{secs:02d}"


    def _add_hover_effect(self, btn):
        original_color = btn.cget("bg")
        btn.bind("<Enter>", lambda e: btn.config(bg=BTN_HOVER, fg="white"))
        btn.bind("<Leave>", lambda e: btn.config(bg=original_color, fg=BTN_FG))
