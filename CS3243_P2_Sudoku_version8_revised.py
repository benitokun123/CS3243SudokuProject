import sys
import copy
import time

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

def puzzleCopy(puzzle):
    puzzle_copy = [[puzzle[i][j] for j in xrange(9)]for i in xrange(9)]
    return puzzle_copy

class Cell:
    def __init__(self, value):
        self.value = value
        self.domain = set()
        self.neighbors = set()

    def __str__(self):
        return str(self.value)

class SudokuPuzzle:
    def __init__(self, matrix, row_constraints, col_constraints, box_constraints, depth):
        self.matrix = matrix
        self.row_constraints = row_constraints
        self.col_constraints = col_constraints
        self.box_constraints = box_constraints
        self.initialize_domains()
        self.initialize_neighbors()
        self.AC_3(dict())
        self.count = 0
        self.no_of_assignment = 0
        self.depth = depth

    def __hash__(self):
        return hash(str(self.matrix))

    def __str__(self):
        out = ""
        for row in range(9):
            for col in range(9):
                out = out + " " + str(self.matrix[row][col])
            out = out + "\n"
        return out

    #initialize the domain of each cell inside the Sudoku puzzle
    def initialize_domains(self):
        for row in range(9):
            for col in range(9):
                domain = self.row_constraints[row].intersection(self.col_constraints[col],
                                                                self.box_constraints[row//3][col//3])
                self.matrix[row][col].domain = domain

    # initialize the neighbors of each cell inside the Sudoku puzzle
    def initialize_neighbors(self):
        for row in range(9):
            for col in range(9):
                self.matrix[row][col].neighbors = self.find_neighbors(row, col)

    # find all unassigned neighbor cells of the cell at coordinate (row, col)
    def find_neighbors(self, row, col):
        neighbors = set()
        for i in range(9):
            if i != row and self.matrix[i][col].value == 0:
                neighbors.add((i, col))
            if i != col and self.matrix[row][i].value == 0:
                neighbors.add((row, i))
        box_row = row // 3 * 3
        box_col = col // 3 * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if i != row and j != col and self.matrix[i][j].value == 0:
                    neighbors.add((i, j))
        return neighbors

    # choose the coordinate of the next cell to be assigned
    # heuristics: Most Constrained Variable and Most Constraining Variable
    def choose_cell_to_assign(self):
        min_domain = 100
        max_degree = -1
        chosen_row = None
        chosen_col = None
        for row in range(9):
            for col in range(9):
                if self.matrix[row][col].value == 0:
                    domain_size = len(self.matrix[row][col].domain)
                    if domain_size < min_domain:
                        min_domain = domain_size
                        chosen_row = row
                        chosen_col = col
                    elif domain_size == min_domain:
                        degree = len(self.matrix[row][col].neighbors)
                        if degree > max_degree:
                            max_degree = degree
                            chosen_row = row
                            chosen_col = col
        return (chosen_row, chosen_col)

    # assign a value to a cell, update domains and neighbors set, and record domain changes
    def assign(self, row, col, new_value, domain_changes):
        self.no_of_assignment += 1
        self.depth += 1
        self.matrix[row][col].value = new_value

        # update domains and neighbor set for the neighbor cells of (row, col)
        for i, j in self.matrix[row][col].neighbors:
            self.matrix[i][j].neighbors.remove((row, col))
            if new_value in self.matrix[i][j].domain and self.matrix[i][j].value == 0:
                self.matrix[i][j].domain.remove(new_value)
                if domain_changes.has_key((i, j)):
                    domain_changes[(i, j)].add(new_value)
                else:
                    domain_changes[(i, j)] = set([new_value])

        # only runs AC_3 at after every 20 assignments
        if self.no_of_assignment % 20 == 0:
            self.AC_3(domain_changes)

    # unassign a value from a cell and revert changes to domains and neighbors set
    def undo_assign(self, row, col, domain_changes):
        self.no_of_assignment -= 1
        self.depth -= 1
        self.matrix[row][col].value = 0
        for i, j in self.matrix[row][col].neighbors:
            self.matrix[i][j].neighbors.add((row, col))
        self.undo_domain_changes(domain_changes)

    # check if the current sudoku state is solvable
    def is_valid(self):
        for i in range(9):
            for j in range(9):
                if self.matrix[i][j].value == 0 and len(self.matrix[i][j].domain) == 0:
                    return False
        return True

    # Initialize every arc among unassigned cells
    def intitializeAC3_queue(self):
        queue = list()
        for row in range(9):
            for col in range(9):
                if self.matrix[row][col].value != 0:
                    continue
                for neighbor_row, neighbor_col in self.matrix[row][col].neighbors:
                    if len(self.matrix[neighbor_row][neighbor_col].domain) == 1 and self.matrix[row][col].value == 0:
                        queue.append(((row, col), (neighbor_row, neighbor_col)))
        return queue

    # Revise the domains of two cells with the arc between (row, col) and (neighbor_row, neighbor_col)
    # Pre-condition: domain of (neighbor_row, neighbor_col) has only 1 value
    def revise(self, row, col, neighbor_row, neighbor_col, domain_changes):
        domain1 = self.matrix[row][col].domain
        domain2 = self.matrix[neighbor_row][neighbor_col].domain
        revise = False
        if len(domain2) != 1:
            return False
        for value in domain2:
            if value in domain1:
                domain1.remove(value)
                if domain_changes.has_key((row, col)):
                    domain_changes[(row, col)].add(value)
                else:
                    domain_changes[(row, col)] = set([value])
                revise = True
        return revise

    # Update the queue with more arcs
    def update_queue(self, queue, row, col, neighbor_row, neighbor_col):
        for (i, j) in self.matrix[row][col].neighbors:
            if (i, j) != (row, col) \
                    and (i, j) != (neighbor_row, neighbor_col) \
                    and self.matrix[i][j].value == 0:
                queue.append(((i, j), (row, col)))

    def AC_3(self, domain_changes):
        queue = self.intitializeAC3_queue()
        while queue:
            (row, col), (neighbor_row, neighbor_col) = queue.pop(0)
            if self.revise(row, col, neighbor_row, neighbor_col, domain_changes):
                if len(self.matrix[row][col].domain) == 0:
                    return False
                if len(self.matrix[row][col].domain) == 1:
                    self.update_queue(queue, row, col, neighbor_row, neighbor_col)
            # print(str(row) + " " + str(col) + " " + str(neighbor_row) + " " + str(neighbor_col))
        return True

    def undo_domain_changes(self, domain_changes):
        for (row, col), changes in domain_changes.items():
            while changes:
                self.matrix[row][col].domain.add(changes.pop())

    def backtrack_search(self):
        self.count += 1
        if self.is_answer():
            return True
        if not self.is_valid():
            return False
        (row, col) = self.choose_cell_to_assign()
        domain_copy = self.matrix[row][col].domain.copy()
        for new_value in domain_copy:
            domain_changes = dict()
            self.assign(row, col, new_value, domain_changes)
            result = self.backtrack_search()
            if result is True:
                return True
            else:
                self.undo_assign(row, col, domain_changes)

    def is_answer(self):
        for row in range(9):
            for col in range(9):
                if self.matrix[row][col].value == 0:
                    return False
        return True

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle  # self.puzzle is a list of lists
        self.ans = puzzleCopy(puzzle)  # self.ans is a list of lists

        self.depth = 0 # depth represent the number of cells that have been assigned value

        self.matrix = self.initialize_cells(self.puzzle)

        self.row_constraints = [set([1, 2, 3, 4, 5, 6, 7, 8, 9]) for i in
                                range(9)]  # set of values that haven't appeared in each row
        self.col_constraints = [set([1, 2, 3, 4, 5, 6, 7, 8, 9]) for i in
                                range(9)]  # set of values that haven't appeared in each collumn
        self.box_constraints = [[set([1, 2, 3, 4, 5, 6, 7, 8, 9]) for i in range(3)] for j in
                                range(3)]  # set of values that haven't appeared in each 3x3 box

        self.initialize_constraints()

    # initialize the value inside each cell with given input
    def initialize_cells(self, puzzle):
        matrix = [[Cell(0) for i in range(9)] for j in range(9)]
        for row in range(9):
            for col in range(9):
                matrix[row][col].value = puzzle[row][col]
        return matrix

    # initialize the row, collumn, and 3x3 box constraints of the Sudoku puzzle
    def initialize_constraints(self):
        for row in range(9):
            for col in range(9):
                value = self.matrix[row][col].value
                if value != 0:
                    self.depth += 1
                    self.row_constraints[row].remove(value)
                    self.col_constraints[col].remove(value)
                    self.box_constraints[row // 3][col // 3].remove(value)

    def solve(self):
        # TODO: Write your code here
        start_time = time.time()
        sudokuPuzzle = SudokuPuzzle(self.matrix, self.row_constraints, self.col_constraints, self.box_constraints, self.depth)
        sudokuPuzzle.backtrack_search()
        end_time = time.time()
        print("Version: BackTracking Search + Reduced AC3 + Most Constrained + Most Constraining Variable")
        print("Time elapsed " + str(end_time - start_time))
        print("Number of states traversed: " + str(sudokuPuzzle.count))
        return sudokuPuzzle.matrix

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.

if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
