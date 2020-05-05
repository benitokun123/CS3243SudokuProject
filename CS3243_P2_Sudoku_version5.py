import sys
import copy
import collections
import time


def puzzleCopy(puzzle):
    puzzle_copy = [[puzzle[i][j] for j in xrange(9)]for i in xrange(9)]
    return puzzle_copy

def setCopy(values):
    set_copy = set()
    for value in values:
        set_copy.add(value)
    return set_copy

def AC3(domains, neighbours, domains_changes):
    q = collections.deque()

    for i in range(0, 81):
        for x in neighbours[i]:
            if len(domains[x]) == 1:
                q.append([i, x])

    while q:
        x, y = q.popleft()
        if len(domains[y]) == 1 and revise(domains, x, y, domains_changes):
            if len(domains[x]) == 0:
                return False
            if len(domains[x]) == 1:
                for z in neighbours[x]:
                    if z != y :
                        q.append([z, x])

    return domains

def revertAC3(domains, domains_changes):
    for key, changes in domains_changes.items():
        while changes:
            domains[key].add(changes.pop())


def revise(domains, x, y, domains_changes):
    result = False
    for d in domains[y]:
        if d in domains[x]:
            if domains_changes.has_key(x):
                domains_changes[x].add(d)
            else:
                domains_changes[x] = set([d])
            domains[x].remove(d)
            result = True
    return result

def generateNeighbours():
    allNeighbours = dict()
    for i in range(0, 81):
        yourNeighbours = set()
        row = i // 9
        col = i % 9
        for j in range(0, 9):
            yourNeighbours.add(row * 9 + j)
            yourNeighbours.add(col + 9 * j)
        starter = 27 * (row // 3) + 3 * (col // 3)
        for j in range(0, 3):
            for k in range(0, 3):
                yourNeighbours.add(starter + j * 9 + k)
        yourNeighbours.remove(i)
        allNeighbours[i] = yourNeighbours
    return allNeighbours
    
   
def backtracksearch(domains, neighbours):
    if domains is False:
        return False
    min_domain = 10
    min_key = 82
    count = 0
    for key,x in domains.items():
        if len(x) == 1:
            count+=1
        else: 
            if len(x) < min_domain:
                min_domain = len(x)
                min_key = key

    if count == 81:
        return domains
    

    #if all(len(x) == 1 for x in domains.values()):
        #return domains
    #val,key = min((len(domains[key]), key) for key in domains if len(domains[key]) > 1)
    domain_copy = setCopy(domains[min_key])
    for d in domain_copy:
        domains[min_key] = set([d])
        domains_changes = dict()

        result = backtracksearch(AC3(domains, neighbours, domains_changes), neighbours)
        if result is False:
            domains[min_key] = domain_copy
            revertAC3(domains, domains_changes)

        else:
            return result
    return False

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = puzzleCopy(puzzle) # self.ans is a list of lists

    def solve(self):
        #Generate domains
        start_time = time.clock()
        domains = dict()
        for i in range(0, 9):
            for j in range(0, 9):
                if self.ans[i][j] == 0:
                    domains[i * 9 + j] = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
                else:
                    domains[i * 9 + j] = set([self.ans[i][j]])
        
        neighbours = generateNeighbours()
        if AC3(domains, neighbours, dict()):

            domains = backtracksearch(domains,neighbours)
            end_time = time.clock()
            print("Time elapsed " + str(end_time - start_time))

            for x, y in domains.items():
                #print(x, y)
                self.ans[x // 9][x % 9] = y.pop()
                # don't print anything here. just resturn the answer
                # self.ans is a list of lists

            return self.ans

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY

if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python sudoku_A2_xx.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python sudoku_A2_xx.py input.txt output.txt\n")
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
