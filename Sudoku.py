import queue
from sys import stdout


class Sudoku:
    numbers = '123456789'
    columns = "123456789"
    rows = "ABCDEFGHI"

    def __init__(self, board):
        self.squares = self.concatenation(self.rows, self.columns)
        self.domains = {
            square: self.numbers if board[i] == '.' else board[i] for i, square in enumerate(self.squares)
        }
        self.neighbors = self.get_neighbors()
        self.pruned = {square: list() if board[i] == '.' else [int(board[i])] for i, square in enumerate(self.squares)}
        self.constraints = {(square, connection) for square in self.squares for connection in self.neighbors[square]}

    def get_neighbors(self):
        vertical_parts = [Sudoku.concatenation(Sudoku.rows, c) for c in Sudoku.columns]
        horizontal_parts = [Sudoku.concatenation(r, Sudoku.columns) for r in Sudoku.rows]
        boxes = [Sudoku.concatenation(rs, cs) for rs in (Sudoku.rows[0:3], Sudoku.rows[3:6], Sudoku.rows[6:9]) for cs in
                 (Sudoku.columns[0:3], Sudoku.columns[3:6], Sudoku.columns[6:9])]
        all_parts = vertical_parts + horizontal_parts + boxes
        all_parts = dict((s, [u for u in all_parts if s in u]) for s in self.squares)
        return dict((s, set(sum(all_parts[s], [])) - {s}) for s in self.squares)

    @staticmethod
    def concatenation(first, second):
        return [a + b for a in first for b in second]

    def conflicts(self, square, domain):
        count = 0
        for neighbor in self.neighbors[square]:
            domains = self.domains[neighbor]
            if len(domains) > 1 and domain in domains:
                count += 1
        return count

    def forward_check(self, square_mrv, square, squares_dict):
        for neighbor in self.neighbors[square_mrv]:
            if neighbor not in squares_dict:
                if square in self.domains[neighbor]:
                    self.domains[neighbor] = self.domains[neighbor].replace(square, '')
                    self.pruned[square_mrv].append((neighbor, square))

    def unassign(self, tile, tiles_dict):
        if tile in tiles_dict:
            for (D, v) in self.pruned[tile]:
                self.domains[D] = self.domains[D] + v

            self.pruned[tile] = []

    def end_status(self):
        for square in self.squares:
            domains = self.domains[square]
            if domains == '' or len(domains) > 1:
                return False
        return True

    def show(self):
        initial_board = ''
        for tile in self.squares:
            initial_board += self.domains[tile]
        solved = ''
        for index, num in enumerate(initial_board):
            solved += num
            if (index + 1) % 9 == 0:
                solved += '\n'
            else:
                solved += ' '
        stdout.write(solved)


def backtrack(sudoku, squares_dict={}):
    if len(squares_dict) == len(sudoku.squares):
        return squares_dict

    #MRV
    unassigned = [square for square in sudoku.squares if square not in squares_dict]
    mrv_square = min(unassigned, key=lambda x: len(sudoku.domains[x]))

    #LCV
    lcv_squares = None
    if len(sudoku.domains[mrv_square]) == 1:
        lcv_squares = sudoku.domains[mrv_square]
    else:
        lcv_squares = sorted(sudoku.domains[mrv_square], key=lambda x: sudoku.conflicts(mrv_square, x))

    for number in lcv_squares:
        if backtrack_consistent(sudoku, squares_dict, mrv_square, number):
            sudoku.forward_check(mrv_square, number, squares_dict)
            squares_dict[mrv_square] = number

            filled_board = backtrack(sudoku, squares_dict)
            if filled_board:
                return filled_board

            sudoku.unassign(mrv_square, squares_dict)
            del squares_dict[mrv_square]
    return False


def backtrack_consistent(sudoku, squares_dict, mrv_square, number):
    for key, val in squares_dict.items():
        if val == number and key in sudoku.neighbors[mrv_square]:
            return False
    return True


def ac3(sudoku):
    arc_queue = queue.Queue()
    for constraint in sudoku.constraints:
        arc_queue.put(constraint)

    while not arc_queue.empty():
        (arc_1, arc_2) = arc_queue.get()
        if revise(sudoku, arc_1, arc_2):
            if len(sudoku.domains[arc_1]) == 0:
                return

            for arc in (sudoku.neighbors[arc_1] - {arc_2}):
                arc_queue.put((arc, arc_1))
    return


def revise(sudoku, arc_1, arc_2):
    for x in set(sudoku.domains[arc_1]):
        if not ac3_consistent(sudoku, x, arc_1, arc_2):
            sudoku.domains[arc_1] = sudoku.domains[arc_1].replace(x, '')
            return True
    return False


def ac3_consistent(sudoku, x, xi, xj):
    for y in sudoku.domains[xj]:
        if xj in sudoku.neighbors[xi] and y != x:
            return True
    return False


board = ''
for i in range(9):
    board += input().replace(' ', '')
sudoku_board = Sudoku(board)
ac3(sudoku_board)
if sudoku_board.end_status():
    sudoku_board.show()
else:
    sudoku_board.domains = backtrack(sudoku_board)
    if sudoku_board.end_status():
        sudoku_board.show()
    else:
        print('Cant Solve')