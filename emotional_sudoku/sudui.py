import math
import curses
import random
from random import shuffle
from past.builtins import (str as oldstr, range, reduce,
                               raw_input, xrange)
screen = curses.initscr()

board_size = 9
board_startPos = 3,3

def InitCurses():
    '''Curses related stuff'''
    global screen
    screen = curses.initscr()
    curses.noecho()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    screen.keypad(1)


class Board():
    '''The game board'''
    def __init__(self,y,x):
        self.Board = [] # create the Board
        self.Board_x = x # lines
        self.Board_y = y # columns
        for i in range(0,y): # create the Board columns
            self.Board.append([])



class GameBoard(Board):
    '''The game board'''
    def __init__(self,y,x):
        Board.__init__(self,y,x)
        self.Number = Number(0)
        self.Fill()
            

    def Fill(self):
        '''Fill the board with random numbers so we can create random Sudoku'''
        for y in range(0,self.Board_y): # first we fill the board with 0's
            for x in range(0,self.Board_x):
                self.Board[y].append(Number(0))

    def Print(self):
        '''Method to print our game board'''
        screen.addstr("\n\n"); # get a space for the information message 
        screen.addstr(" -------------------------------\n", curses.color_pair(5)) 
        for x in range(0,self.Board_x):
            screen.addstr(" |", curses.color_pair(5))
            for y in range(0,self.Board_y):
                if self.Board[x][y].getNumber() != 0:
                    self.Board[x][y].printNumber()
                else:
                    screen.addstr("   ")
                if y == 2 or y == 5:
                    screen.addstr("|", curses.color_pair(5))
            screen.addstr("|\n", curses.color_pair(5) )
            if x == 2 or x == 5:
                screen.addstr(" -------------------------------\n", curses.color_pair(5) | curses.A_BOLD) 
        screen.addstr(" -------------------------------\n", curses.color_pair(5) | curses.A_BOLD) 

    def setNumber(self, x, y, number, state):
        '''Set the desired number and lock it if True'''
        self.Board[x][y] = Number(number)
        if state:
            self.Board[x][y].setLock()

    def Play(self,x,y, number):
        '''The play method :)'''
        if self.Board[x][y].getNumber() == 0 or self.Board[x][y].getState() == 0:
            #if self.CheckNumber(x,y,number) == True:
            self.setNumber(x,y,number,False)
        """
            else:
                ScreenInfo("Bad number :)",2)
                screen.getch()				
        else:
            ScreenInfo("Can't play here!",2)
            screen.getch()
        """




class Number:
    '''Object number'''		
    def __init__(self, suit):
        self.suit = suit
        self.state = 0

    def setLock(self):
        '''Set locked on or not'''
        if self.state == 0:
            self.state = 1
        else:
            self.state = 0	

    def getState(self):
        '''Return if it is locked or not'''
        return self.state
        
    def getNumber(self):
        '''Return the number'''
        return self.suit

    def printNumber(self):
        '''Print the number'''
        if self.getState() == 1:
            screen.addstr(" %s " % self.getNumber(), curses.color_pair(4))
        elif self.getState() == 0:
            screen.addstr(" %s " % self.getNumber(), curses.color_pair(1))		



class Table:
    '''Table where we play. The board is in the table and the players are sitting right next to it :)'''	
    def __init__(self):
        self.Board = GameBoard(9,9)
        #self.Cursor = MoveCursor(3,3,3,3,1,1,3,13,3,29) # give the rules to MoveCursor Object
        self.Cursor = MoveCursor(3,3) # give the rules to MoveCursor Object
        
        self.ChosenColumn = 0 # my dchosen column
        self.ChosenRow = 0 # my chosen row
        self.Think() # The main
        
    def ChosenRowColumn(self, row, column):
        m = 8
        '''A method to get the right Row and Column to put the number and control the jump the cursor have to do in the game'''
        self.ChosenRow = row
        self.ChosenColumn = column		
        if self.ChosenRow < 0:
            self.ChosenRow = m
        elif self.ChosenRow > m:
            self.ChosenRow = 0
        elif self.ChosenColumn < 0:
            self.ChosenColumn = m
        elif self.ChosenColumn > m:
            self.ChosenColumn = 0
            
    def ForceBorderJump(self, keypress):
        '''Force the jump in the border when moving the cursor'''
        if keypress == 'right':
            if self.Cursor.get_x() == 12 or self.Cursor.get_x() == 22:
                self.Cursor.x = self.Cursor.get_x()+1
        elif keypress == 'left':
            if self.Cursor.get_x() == 10 or self.Cursor.get_x() == 20:
                self.Cursor.x = self.Cursor.get_x()-1
        elif keypress == 'up':
            if self.Cursor.get_y() == 6 or self.Cursor.get_y() == 10:
                self.Cursor.y = self.Cursor.get_y()-1
        elif keypress == 'down':
            if self.Cursor.get_y() == 6 or self.Cursor.get_y() == 10:
                self.Cursor.y = self.Cursor.get_y()+1

    def Think(self):
        '''Method where we read the keyboard keys and think in the game :P'''
        list = [ ] # create a list with numbers from 9 to 1. We will get the index from the event. example: 57-49=8, but the 8 number is the number 1 so we reverse the list so the index is correct :)
        for i in range (1,10):
            list.append(i)
        list.reverse()
        while True:
            screen.clear()
            self.Board.Print()
            #if self.Board.SomebodyWonPopcorn(): # checks if he won :P
             #   ScreenInfo("YOU WIIIIIIIIN!!! :)",2)
              #  screen.getch()
               # break
            self.Cursor.Move('actual')
            event = screen.getch()
            if event == ord("q"): 
                break
            elif event == curses.KEY_LEFT:
                self.Cursor.Move('left')
                self.ChosenRowColumn(self.ChosenRow,self.ChosenColumn-1)
                self.ForceBorderJump('left')
            elif event == curses.KEY_RIGHT:
                self.Cursor.Move('right')
                self.ChosenRowColumn(self.ChosenRow,self.ChosenColumn+1)
                self.ForceBorderJump('right')
            elif event == curses.KEY_UP:
                self.Cursor.Move('up')
                self.ChosenRowColumn(self.ChosenRow-1,self.ChosenColumn)
                self.ForceBorderJump('up')
            elif event == curses.KEY_DOWN:
                self.Cursor.Move('down')
                self.ChosenRowColumn(self.ChosenRow+1,self.ChosenColumn)
                self.ForceBorderJump('down')
            elif event >= 49 and event <= 57: # from 1 to 9
                self.Board.Play(self.ChosenRow,self.ChosenColumn,list[57-event]) # list[57-event] is the right number from the keyboard
            elif event == ord("s"): # S key
                self.Board.Solve(0,0,False)



class MoveCursor:
    '''
    An object to move the cursor with rules 
    Usage: MoveCursor(initial x position, initial y position, move left jump size, move right jump size, go up jump size, go down jump size, up limit size, down limit size, left limit size, right limit size) 
    '''
    board_size = 9
    jumplen_hor = 3
    jumplen_ver = 1


    def __init__(self, init_x, init_y):
        self.x = init_x
        self.y = init_y
        self.leftbound = init_x
        self.rightbound = init_x + (self.jumplen_hor * board_size) -1
        self.upperbound = init_y
        self.lowerbound = init_y + (self.jumplen_ver * board_size) -1



    """
    def __init__(self,initial_x,initial_y,left,right,up,down,x_up_max,x_down_max,y_left_max,y_right_max):
        self.x           = initial_x
        self.y           = initial_y
        self.initial_x   = initial_x
        self.initial_y   = initial_x
        self.move_left   = left
        self.move_right  = right
        self.move_up     = up
        self.move_down   = down
        self.x_up_max    = x_up_max
        self.y_left_max  = y_left_max
        self.x_down_max  = x_down_max
        self.y_right_max = y_right_max
    """
    def MoveLeft(self):
        self.x = self.x - self.jumplen_hor
        if self.x < self.leftbound:
            self.x = self.rightbound

    def MoveRight(self):
        self.x = self.x+self.jumplen_hor
        if self.x > self.rightbound:
            self.x = self.leftbound

    def MoveUp(self):
        self.y = self.y-self.jumplen_ver

    def MoveDown(self):
        self.y = self.y+self.jumplen_ver


    def MoveActual(self):
        screen.move(self.y,self.x)
        
    def Move(self,option):
        if option == 'left':
            self.MoveLeft()
        elif option == 'right':
            self.MoveRight()
        elif option == 'up':
            self.MoveUp()
        elif option == 'down':
            self.MoveDown()
        elif option == 'initial':
            self.MoveInitial()
        elif option == 'actual':
            self.MoveActual()
        else:
            Quit()
    
    def get_x(self):
        '''Return X position'''
        return self.x
        
    def get_y(self):
        '''Return Y position'''
        return self.y

def Quit():
    '''Quiiiiiiiit!!!'''
    curses.endwin()
    quit()

class Menu:
    ''''Where everything begins, the Menu (main too)'''	
    def __init__(self):
        #self.Cursor = MoveCursor(2,0,0,0,1,1,2,5,0,0) # give the rules to MoveCursor Object
        self.Cursor = MoveCursor(2,0) # give the rules to MoveCursor Object
        
        self.main()

    def henshin_a_gogo_baby(self):
        '''A name inspired in Viewtiful Joe game, lol. It checks the cursor position and HENSHIN A GOGO BABY'''
        #if self.Cursor.get_x() == 2:
        gogo = Table()
        if self.Cursor.get_x() == 5:
            Quit()
    
    def main(self):
        '''The main :|'''
        while True:
            
            screen.clear()
            self.henshin_a_gogo_baby()
            event = screen.getch()
            #self.henshin_a_gogo_baby()
            if event == ord("q"): 
                Quit()
            """
            screen.addstr(" Sudoku \n\n", curses.color_pair(3))
            screen.addstr("  Play\n")
            screen.addstr("  Help\n")
            screen.addstr("  About\n")
            screen.addstr("  Quit\n")
            
            
            self.Cursor.Move('actual')
            event = screen.getch()
            #self.henshin_a_gogo_baby()
            if event == ord("q"): 
                Quit()
            elif event == curses.KEY_UP:
                self.Cursor.Move('up')
            elif event == curses.KEY_DOWN:
                self.Cursor.Move('down')
            elif event == 10:
                self.henshin_a_gogo_baby()
            """

if __name__ == '__main__': 

    InitCurses()
    run_for_your_life = Menu() # The menu
    curses.napms(3000)
    curses.endwin()