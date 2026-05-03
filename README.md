**AI-1 Spring 26 Project Proposal**

**Team Members**

| Name in ARABIC | Section No |
| ----- | :---: |
| **احمد فايق ابراهيم سلام** | **1** |
| **السيد على السيد عاشور** | **2** |
| **رامز عبدالبديع منير عبدالبديع سليمان** | **3** |

**Team ID (  47  )**

**Idea Short Name ( Sudoku-CSP )**

**Idea Description**

|  A Sudoku puzzle game that models the puzzle as a Constraint Satisfaction Problem (CSP). The system generates unique puzzles, allows the user to solve them manually, and includes an AI solver that uses Backtracking Search enhanced with MRV (Minimum Remaining Values) and Forward Checking to find the solution automatically.  |
| :---- |

**Agent Architecture**

- [ ] Simple Reflex Agent  
- [ ] Model-Based Reflex Agent  
- [x] Goal-Based Agent  
- [ ] Utility-Based Agent

Why: The agent has a clear goal — find a complete legal assignment for all empty cells where no constraint is violated. It acts by trying number assignments and evaluating whether constraints are satisfied, which is exactly goal-based behavior.

**Problem-Solving Framework**

- [ ] Classical Search  
- [ ] Local Search (Optimization)  
- [ ] Adversarial Search (Two-Player Games)  
- [x] Constraint Satisfaction Problem

Why: Sudoku is defined by variables (cells), domains (1–9), and constraints (no duplicates in row/column/box) — this is the exact definition of CSP.

**Proposed Algorithm(s)**

|  1\. Backtracking Search — the core solver. 2\. MRV — Minimum Remaining Values — selects which cell to fill next by choosing the one with the fewest valid numbers remaining. 3\. Forward Checking — after each assignment, checks if any neighboring cell's domain becomes empty, and backtracks immediately.  |
| :---- |

**PEAS**

| Puzzle solved correctly, number of backtracks, and solving time | Performance Measures |
| :---- | :---- |
| The 9×9 Sudoku board with pre-filled cells | **Environment** |
| Filling a cell with a number, highlighting errors, and displaying the solution | **Actuators** |
| Reading the current board state, detecting empty cells, and reading user input | **Sensors** |

**Environment Properties**

| Property | Choice | Reason |
| :---: | :---: | ----- |
| Observable | Fully Observable | The entire board is always visible |
| Deterministic | Deterministic | The same input always gives the same output |
|  | Strategic | No randomness in solving decisions |
| Discrete | Discrete | Finite cells, finite domain {1–9} |
| Agent | Single-Agent | One solver, no opponent |
| Episodes | Sequential | Each cell assignment affects future choices |
| Change | Static | The board doesn't change while the agent thinks |
