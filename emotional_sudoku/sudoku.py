'''
1. fill one box randomly
2. fill diagonal randomly
'''

import random as rand

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

def hasDuplicateSudoku(gridList, grid):
    counter = 0
    for i in range(len(gridList)):
        counter = 0
        for j in range(len(grid)):
            if grid[j] == gridList[i][j]:
                counter += 1
    if counter >= len(grid):
        return True
    else: 
        return False

#print(hasDuplicateSudoku([[0,0],[1,1]],[0,1]))

def createSudokus(numberOfSudokus):
    n = numberOfSudokus
    sudokus = []    # list of grids

    for j in range(n):
        grid = [[] for i in range(4)]   # creates empty grid
        fillBox(grid)               # fills top left box randomly
        fillDiagonal(grid)          # fills the diagonal randomly
        fillRest(grid)              # fills rest with zeros
        # check if grid is in grids
        #sudokus.append(grid)
        
        if not hasDuplicateSudoku(sudokus,grid):
            sudokus.append(grid)
            print("Sudoku No.",len(sudokus))
            displaySudoku(grid)         # prints the sudoku grid
        #else:
            #print("dup")
        
    return sudokus
        
'''
def removeDuplicateSudokus(sList):
    for i in sList:
        for j in sList:
'''   


sudokus = createSudokus(10)

print(len(sudokus))
# save sudokus as a list of grids