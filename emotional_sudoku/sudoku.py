'''
1. fill one box randomly
2. fill diagonal randomly
3. fill rest according to sudoku rules
'''

import random as rand

# method for filling a box randomly
def fillBox():
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
def fillDiagonal():
    
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
def fillRest():
    for col in grid:
        while len(col) < 4:
            col.append(0)

# method for displaying sudoku grid
def displaySudoku():
    for col in grid:
        print(col)


grid = [[] for i in range(4)]   # creates empty grid
fillBox()               # fills top right box randomly
fillDiagonal()          # fills the diagonal randomly
fillRest()              # fills rest with zeros
displaySudoku()         # prints the sudoku grid