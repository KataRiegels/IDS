'''
1. Create a sudoku:
    1.1. fill one box randomly
    1.2. fill diagonal randomly
2. Only add distinct sudokus to a list
'''

import random as rand
import pickle

# method for filling a box randomly
def fillBox(grid):
    numberOfRows = 4
    a = []
    s = set()
    while len(a) < numberOfRows:
        # get random number
        num = rand.randint(1,numberOfRows)
        # if number hasn't been used yet, add it to array and set
        if num not in s:
            a.append(num)
            s.add(num)
    grid[0].append(a[0])
    grid[0].append(a[1])
    grid[1].append(a[2])
    grid[1].append(a[3])

# method for filling the diagonal randomly
# (padded with zeros)
def fillDiagonal(grid):
    
    num1 = rand.randint(1,4)
    for i in range(2):
        grid[2].append(0)
    grid[2].append(num1)

    num2 = rand.randint(1,4)
    while num2 == num1:
        num2 = rand.randint(1,4)

    for i in range(3):
        grid[3].append(0)
    grid[3].append(num2)

# method for filling the rest with zeros
def fillRest(grid):
    for col in grid:
        while len(col) < 4:
            col.append(0)

# method for displaying sudoku grid
def displaySudoku(grid):
    for col in grid:
        print(col)

# method for creating different sudokus (n tries)
def createSudokus(numberOfSudokus):
    n = numberOfSudokus
    sudokus = []    # list of grids

    for j in range(n):
        grid = [[] for i in range(4)]   # creates empty grid
        fillBox(grid)                   # fills top left box randomly
        fillDiagonal(grid)              # fills the diagonal randomly
        fillRest(grid)                  # fills rest with zeros     
        if not contains(sudokus,grid):
            sudokus.append(grid)
            #print("Sudoku No.",len(sudokus))
            #displaySudoku(grid)         # prints the sudoku grid
    return sudokus 

# method for checking if two lists have the same entries
def sameList(list1, list2):
    counter = 0
    for i in range(len(list1)):
        if list1[i] == list2[i]:
            counter += 1
    if counter >= len(list1):
        return True
    else:
        return False

# method for checking if a list of lists already contains a specific list
def contains(sudokuList, grid):
    for s in sudokuList:
        if sameList(s,grid):
            return True
    return False

# create all 288 possible sudokus, stored in a list
sudokus = createSudokus(2000)
#print(sudokus[0])

# pickling the sudokus
filename = 'sudoku_pickle'
outfile = open(filename,'wb')
pickle.dump(sudokus,outfile)
outfile.close()
