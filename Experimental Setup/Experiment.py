import os
import sys
import csv
from random import shuffle
from random import randint
import A as algoA
import B as algoB
import C as algoC
import D as algoD
import E as algoE

def filePath(path):
    fileList = []
    for file in sorted(os.listdir(path)):
        if file.endswith(".txt"):
            fileList.append(os.path.join(path,file))

    return fileList


def getInputFiles():
    dir_path = os.path.dirname(os.path.realpath('__file__'))
    fileList = []
    path = "/testcases/easy"
    fileList.extend(filePath(dir_path + path))
    path = "/testcases/moderate"
    fileList.extend(filePath(dir_path + path))
    path = "/testcases/difficult"
    fileList.extend(filePath(dir_path + path))
    
    return fileList

def runTests():
    fileList = getInputFiles()
    listoflists = []
    no_test_case = 1
    for file_name in fileList:
        sublist = [no_test_case]
        if (no_test_case - 1) // 5 == 0:
            sublist.append("easy")
        elif (no_test_case - 1) // 5  == 1:
            sublist.append("moderate")
        else:
            sublist.append("hard")
        
        puzzle = extract_puzzle(file_name)

        a = algoA.Sudoku(puzzle)
        a.solve()
        sublist.extend([a.time, a.count])

        b = algoB.Sudoku(puzzle)
        b.solve()
        sublist.extend([b.time, b.count])

        c = algoC.Sudoku(puzzle)
        c.solve()
        sublist.extend([c.time, c.count])

        d = algoD.Sudoku(puzzle)
        d.solve()
        sublist.extend([d.time, d.count])

        e = algoE.Sudoku(puzzle)
        e.solve()
        sublist.extend([e.time, e.count])

        listoflists.append(sublist)
        no_test_case += 1
    return listoflists

def extract_puzzle(file_name):
    try:
        f = open(file_name, 'r')
    except IOError:
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
    return puzzle


if __name__ == "__main__":
     data_lists = runTests()
     dir_path = os.path.dirname(os.path.realpath('__file__'))
     with open(dir_path + "/data.csv",'wb') as f: 
        w = csv.writer(f)
        w.writerow(['Test case','Difficulty Level'
                    'Time (A)', 'Space (A)',
                    'Time (B)', 'Space (B)',
                    'Time (C)', 'Space (C)',
                    'Time (D)', 'Space (D)',
                    'Time (E)', 'Space (E)'])
        w.writerows(data_lists)