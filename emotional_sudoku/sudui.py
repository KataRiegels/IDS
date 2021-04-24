import argparse
import os
import sys
import random
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from cv2 import cv2
import numpy as np

import tensorflow 
from tensorflow.keras.layers import (Conv2D, Dense, Dropout, Flatten, MaxPooling2D)
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D

import subprocess
import math
import curses
import time
import threading

import pickle


screen = curses.initscr()

board_size = 4

def Quit():
    screen.clear()
    screen.addstr(10,30, "Quitting..")
    screen.refresh()
    time.sleep(1)
    curses.endwin()
    quit()


def initializeCurses():
    screen = curses.initscr()
    curses.noecho()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE,    curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN,   curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_CYAN,    curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE,   curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED,     curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_BLACK,   curses.COLOR_GREEN)
    curses.init_pair(8, curses.COLOR_BLACK,   curses.COLOR_RED)
    curses.init_pair(9, curses.COLOR_BLACK,   curses.COLOR_YELLOW)
    curses.init_pair(10, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(11, curses.COLOR_WHITE,  curses.COLOR_MAGENTA)    
    colorpairs = {"blue-black"    : curses.color_pair(1),
                  "green-black"   : curses.color_pair(2),
                  "cyan-black"    : curses.color_pair(3),
                  "white-black"   : curses.color_pair(4),
                  "red-black"     : curses.color_pair(5),
                  "magenta-black" : curses.color_pair(6),
                  "black-green"   : curses.color_pair(7),
                  "black-red"     : curses.color_pair(8),
                  "black-yellow"  : curses.color_pair(9),
                  "yellow-black"  : curses.color_pair(10),
                  "white-magenta" : curses.color_pair(11)}

    curses.curs_set(1)
    screen.keypad(1)
    curses.col = colorpairs


class N:
    '''Object number'''		
    def __init__(self, suit):
        self.suit = suit

    # Converts the numbers into matching emojis
    def convertToEmoji(self,number):
        if number == 0:
            return "DELETE"
        if number == 1:
            return ":D"
        if number == 2:
            return ":o"
        if number == 3:
            return ":*"
        if number == 4:
            return ":("
        else:
            return "ERROR"

    # Return the actual int
    def getNumber(self):
        return self.suit

    # Returns the number converted to emoji
    def numAsEmoji(self):
        return self.convertToEmoji(self.getNumber())

    def __str__(self):
        return self.getNumber()


'''  The sudoku game, which contains a board to print and the update function  '''
class SudokuGame():
    def __init__(self, sud_list, init_x, init_y, horjump = 3, verjump = 1, original_sud = None, nameloc = (0,0)):
        self.sudoku = sud_list
        self.sudoku_size = len(sud_list)
        self.nameloc = nameloc
        self.board = [[N(0)]*self.sudoku_size for i in range(self.sudoku_size)]
        if original_sud == None:
            self.boardCopy = [[0]*self.sudoku_size for i in range(self.sudoku_size)]
        else:
            self.boardCopy = original_sud


        for y in range(self.sudoku_size):
            for x in range(self.sudoku_size):
                self.board[x][y] = N(self.sudoku[x][y])
                if original_sud == None:
                    self.boardCopy[x][y] = self.sudoku[x][y]
        #self.board = self.sudoku
        self.init_x,         self.init_y      = init_x,  init_y
        self.xjump,          self.yjump       = horjump, verjump
        self.current_column, self.current_row = 0,       0
        self.solved = False
        self.relativeY = (self.sudoku_size+self.sudSqrt() )* self.yjump + self.init_y

        self.bar_color    = curses.col["magenta-black"]
        self.input_color  = curses.col["cyan-black"]
        self.locked_color = curses.col["green-black"] 
        self.moveCursor()


       # check row
    def checkRow(self, row):
        row_set = set()
        for num in self.board[row]:
            row_set.add(num.getNumber())
        if 0 in row_set:
            return "unfinished"
        elif len(row_set) < self.sudoku_size:
            return "not valid"
        else:
            return "correct"
 

        # check column
    def checkColumn(self, col):
        col_set = set()
        for row in self.board:
            col_set.add(row[col].getNumber())
        if 0 in col_set:
            return "unfinished"
        elif len(col_set) < self.sudoku_size:
            return "not valid"
        else:
            return "correct"


    # check box
    def checkBox(self, boxCol, boxRow):
        
        box_set = set()
        box = self.accessBox(boxCol, boxRow)
        
        for num in box:
            box_set.add(num)
        if 0 in box_set:
            return "unfinished"
        elif len(box_set) < len(box):
            return "not valid"
        else:
            return "correct"
    
    def checkSudoku(self):
        result = "correct"
        for row in range(self.sudoku_size):
            checkedRow = self.checkRow(row)
            if checkedRow == "unfinished":
                return "unfinished"
            elif checkedRow == "not valid":
                result = "wrong"
        
        for col in range(self.sudoku_size):
            checkedCol = self.checkColumn(col)
            if checkedCol == "unfinished":
                return "unfinished"
            elif checkedCol == "not valid":
                result = "wrong"
        
        for col in range(self.sudSqrt()):
            for row in range(self.sudSqrt()):
                checkedBox = self.checkBox(col,row)
                if checkedBox == "unfinished":
                    return "unfinished"
                elif checkedBox == "not valid":
                    result = "wrong"

        return result
    
    


    def accessBox(self, boxColumn, boxRow):
        startCol = boxColumn * self.sudSqrt()
        startRow = boxRow    * self.sudSqrt()
        l = []
        for i in range(self.sudSqrt()):
            for j in range(self.sudSqrt()):
                l.append(self.board[startCol+j][startRow+i].getNumber())
        return l

  

    ''' Prints the board as it currently is.''' 
    def Print(self):

        hor_square_bars = "  " + "-" * ((self.sudoku_size+self.sudSqrt()) * self.xjump - 1)
        ver_bar = self.printfield("|")
        extraY = 1
        
        
        screen.addstr(self.init_y*self.yjump, self.init_x, hor_square_bars, self.bar_color)        # prints the upper line
        # prints everything on the board as well as the vertical bars and inner horizontal lines
        for y in range(self.sudoku_size):
            # Checking whether there needs to be a horizontal line
            if ((y+1) % self.sudSqrt() == 1) and (y+1 > self.sudSqrt()):
                screen.addstr((self.init_y+y+extraY)*self.yjump, self.init_x, hor_square_bars, self.bar_color)
                extraY += 1
            screen.addstr((self.init_y+y+extraY)*self.yjump, self.init_x, ver_bar, self.bar_color)   # Left-most bar

            for x in range(self.sudoku_size):
                # Checks when to draw bar
            
                if ((x+1) % self.sudSqrt() == 1) and (x+1 > self.sudSqrt()):
                    screen.addstr(ver_bar, self.bar_color)
                # Print either the emoji or whitespaces if cell has not been filled
                if self.board[x][y].getNumber() != 0:
                    if self.cellEditable(x,y):
                        color = self.input_color
                    else:
                        color = self.locked_color
                    screen.addstr(self.printfield(self.board[x][y].numAsEmoji()), color)
                else:
                    screen.addstr(self.printfield(" "))
            screen.addstr(ver_bar, self.bar_color)                                       # right-most bar
        screen.addstr((self.init_y + self.sudoku_size + extraY)*self.yjump, self.init_x, hor_square_bars, self.bar_color) # lower line
        


    ''' Takes a sudoku cell and moves the blinking curser there showing player where they are about to enter emoji.
        Also considers the "jumps" around lines and bars'''
    def sudokuToScreenCoord(self, current_x, current_y):
        outer_x = current_x + math.floor(current_x/math.sqrt(self.sudoku_size))
        outer_y = current_y + math.floor(current_y/math.sqrt(self.sudoku_size))
        inner_x = self.xjump * outer_x + self.init_x + (self.xjump + 1) 
        inner_y = self.yjump * outer_y + self.init_y + (self.yjump) 
        return [inner_x, inner_y]

    ''' Sets the cursor position based on current position on sudoku board    '''
    def moveCursor(self):
        pos = self.sudokuToScreenCoord(self.current_column, self.current_row)
        screen.move(pos[1], pos[0])

    ''' The whole update of the sudoku, such as moving on the table and playing an emoji '''

    def infoPrints(self, arg):
        infotext = curses.col["blue-black"]
        keycolor = curses.col["cyan-black"]
        def pressInfo(ypos, key, instructions, xpos = 5):
            screen.addstr(self.relativeY + ypos, xpos , 'Press ', infotext)
            screen.addstr(key, keycolor)
            screen.addstr(instructions, infotext)
        screen.addstr(self.nameloc[1], self.nameloc[0], "SUDOKU", curses.col["white-magenta"])
        pressInfo(5, "Enter    ", 'to insert emoji: ')
        screen.addstr(N(arg).numAsEmoji(), curses.col["yellow-black"])
        pressInfo(6, "Spacebar ", "to check if your sudoku is correct")
        pressInfo(7, "q        ", " to exit window in focus")

    def messagePrint(self, message, color):
        screen.addstr(self.relativeY + 2, 15, message, curses.col[color])


    def update(self, arg):
        
        screen.clear()
        screen.nodelay(True)
        self.moveCursor()
        self.infoPrints(arg)
        self.Print()
        self.moveCursor()
        event = screen.getch()
        if event == ord("q"): 
            return False
            
        elif event ==  curses.KEY_LEFT or event ==  ord("a"):
            self.current_column -= 1
            if self.current_column < 0:
                self.current_column = self.sudoku_size -1
        elif event == curses.KEY_RIGHT or event ==  ord("d"):
            self.current_column += 1
            if self.current_column > self.sudoku_size -1:
                self.current_column = 0
        elif event == curses.KEY_UP or event ==  ord("w"):
            self.current_row -= 1
            if self.current_row < 0:
                self.current_row = self.sudoku_size -1
        elif event == curses.KEY_DOWN or event ==  ord("s"):
            self.current_row += 1
            if self.current_row > self.sudoku_size -1:
                self.current_row = 0
        elif event == 8:
            if self.cellEditable(self.current_column,self.current_row):     
                self.board[self.current_column][self.current_row] = N(0)
            else:
                self.messagePrint(f'Nice try. That\'s cheating ;-)', "red-black")
                #screen.addstr(self.relativeY + 10, 15, f'Nice try. That\'s cheating ;-)', curses.color_pair(5))  
        elif event == 32:
            screen.nodelay(False)
            result = self.checkSudoku()
            self.isCorrect(result)
            event = screen.getch()
        # If player chooses to use number keys to play with
        elif 48 <= event <= 48 + 9:
            self.moveCursor()
            screen.nodelay(False)
            arg = event-48
            if self.cellEditable(self.current_column,self.current_row):   
                self.messagePrint('psst.. you are about to place a ', 'white-black' )
                screen.addstr( f"{N(arg).numAsEmoji()}", curses.col["yellow-black"])                 
                #screen.addstr(self.relativeY + 10, 15, f'psst.. you are about to place a \"{N(arg).numAsEmoji()}\" here')
            else:
                self.messagePrint(f'Nice try. That\'s cheating    ┻━┻ ~ /(ò_ó/)', 'red-black')
                #screen.addstr(self.relativeY + 10, 15, f'Nice try. That\'s cheating    ┻━┻ ~ /(ò_ó/)', curses.color_pair(5))
            self.Print()
            self.moveCursor()
            event = screen.getch()

            
        # When the player presses enter, play the emoji decided based on camera (or the keyboard number input)
        if event == 10:
            screen.nodelay(False)
            if self.cellEditable(self.current_column,self.current_row):                
                self.board[self.current_column][self.current_row] = N(arg)
            else:
                self.messagePrint("Nice try. That\'s cheating    ┻━┻ ~ /(ò_ó/)", "red-black")
                #screen.addstr(self.relativeY + 10, 15, "Nice try. That\'s cheating    ┻━┻ ~ /(ò_ó/)", curses.color_pair(5))
                event = screen.getch()
                screen.nodelay(True)
                #if event == 10:
                 #   screen.nodelay(True)
            self.Print()   
        self.moveCursor()

    def cellEditable(self, col, row):
        return self.boardCopy[col][row] == 0


    def isCorrect(self, result):
        #ypos = (self.sudoku_size+self.sudSqrt()) * self.yjump + self.init_y + 14
        if result == "correct":
            self.messagePrint("Yay, you won!", "black-green")
            #screen.addstr(self.relativeY + 14, 15, "Yay, you won!", curses.color_pair(7))
            self.solved = True
        elif result == "wrong":
            self.messagePrint("Whoops, there's something wrong here", "black-red")

            #screen.addstr(self.relativeY + 14 , 15, "Whoops, there's something wrong here", curses.color_pair(8) )
        elif result == "unfinished":
            self.messagePrint("The sudoku is not finished, mate", "black-yellow")
        
            
        
    
    # Simply returns the square root of the size
    def sudSqrt(self):
        return int(math.sqrt(self.sudoku_size))

    # Makes sure the input for a cell will stay somewhat in the middle. Flexible on cell-size and input-size
    def printfield(self, inp):
        inp = str(inp)
        left  = " " * ( + int((self.xjump- len(str(inp)))/2))
        right = " " * (self.xjump - len(left) - len(str(inp)))
        return left + inp + right

    def saveGame(self):
        # pickling the sudokus
        filename = 'continue_pickle'
        outfile = open(filename,'wb')
        self.convertToInts()
        save = [self.board, self.boardCopy]
        pickle.dump(save,outfile)
        outfile.close()

    def convertToInts(self):
        for y in range(self.sudoku_size):
            for x in range(self.sudoku_size):
                self.board[x][y] = self.board[x][y].getNumber()



class CamDetection():
        
    def __init__(self):
        self.result = 0

        #load our model
        self.emojimodel = tensorflow.keras.models.load_model('calamari.h5')
        #initialize an array tocontain frame information
        self.emojidata = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        #load our label dictionary
        self.emoji_dict = {0: ":D", 1: ":O", 2:":*", 3:":("}

        #start webcam
        for attempt in range(3):
            try:
                self.cap = cv2.VideoCapture(attempt)
                break
            except Exception as e:
                print(e)

        self.facecasc = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.font = cv2.FONT_HERSHEY_SIMPLEX

        self.counter = {0: 0, 1: 0, 2: 0, 3: 0}

    def get_gpu_temp(self):
        temp = subprocess.check_output(['vcgencmd measure_temp | egrep -o \'[0-9]*\.[0-9]*\''],
                                        shell=True, universal_newlines=True)
        return str(float(temp))


    def thefunction(self):

        # Find haar cascade to draw bounding box around face
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        if not ret:
            return
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.facecasc.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        try:
            for (x, y, w, h) in faces:
                self.emojiframe = cv2.rectangle(frame, (x-10, y-50), (x+w+10, y+h+30), (255, 0, 0), 2)
                frame3 = frame[y-50:y + h + 10, x-10:x + w +10]
                frame3 = cv2.resize(frame3, (224, 224))
                image_array2 = np.asarray(frame3)
                self.emojidata[0]=(image_array2.astype(np.float32) / 127.0) - 1
                emoji = self.emojimodel.predict(self.emojidata)
                #print(emoji)
                emojiresult = np.argmax(emoji[0])
                self.counter[emojiresult] += 1
                cv2.putText(frame, self.emoji_dict[int(emojiresult)], (x,y), self.font, 1.7, (0, 255, 0), 2, cv2.LINE_AA)
        except Exception as e:
            print(str(e))
        '''
        try:
            path=os.path.join(mypath,n)
            img=cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            img=cv2.resize(img, (img_rows,img_cols))

        except Exception as e:
            print(str(e))
        '''
        cv2.imshow('video', cv2.resize(frame, (800, 480), interpolation=None))   # interpolation = None?
        
        for i in self.counter:
            if self.counter[i] >= 10:
                self.result = i
                for i in self.counter:
                    self.counter[i] = 0


class SudokuReader():
    def __init__(self,filename, rand = False):
        self.filename = filename
        self.sudoku_list = None
        self.rand = rand
        self.read()

    def read(self):
        infile = open(self.filename,'rb')
        self.sudoku_list = pickle.load(infile)
        infile.close()

    def extract(self,  index = 0):
        
        if self.rand:
            index = random.randint(0,len(self.sudoku_list)-1)
        self.sudoku = self.sudoku_list[index]
        print(self.sudoku)
        return self.sudoku






class Menu():
    class Option():
        def __init__(self, name, functionality):
            self.name = name
            self.functionality = functionality
            self.game = None

        def pickOption(self):
            self.functionality()
            
    def __init__(self, init_x, init_y):
        self.locationpos = (10, 2)
        self.init_x = init_x 
        self.init_y = init_y + self.locationpos[1]
        screen.nodelay(False)
        
        newGame  = self.Option("New game",           self.startNewGame)
        contGame = self.Option("Continue last game", self.loadGame)
        helpGame = self.Option("How to play",        self.getHelp)
        quitGame = self.Option("Quit",               self.quitApp)
        self.options = [newGame, contGame, helpGame, quitGame]
        self.rowNr = 0
        self.STOP = False
        self.startMenu()
        

    def moveCursor(self):
        screen.addstr(self.locationpos[1], self.locationpos[0], "MENU", curses.col["white-magenta"] | curses.A_BOLD)
        while True:
            screen.nodelay(True)
            event = screen.getch()

            screen.move(self.init_y + self.rowNr, self.init_x)
            if event == ord("r"): # Shouldn't be used, but is there to make sure quitting is possible in the menu
                Quit()
            elif event == 10:
                self.options[self.rowNr].pickOption()
            if event == curses.KEY_DOWN:
                self.rowNr += 1
                if self.rowNr >= len(self.options):
                    self.rowNr = 0
            if event == curses.KEY_UP:
                self.rowNr -= 1
                if self.rowNr < 0:
                    self.rowNr = len(self.options) -1

    def startNewGame(self):
        sudoku    = SudokuReader('sudoku_pickle', rand = True).extract()
        self.game = SudokuGame(sudoku,13,3 + self.locationpos[1], nameloc = self.locationpos)
        self.goGame()
  
 

    def goGame(self):
        screen.clear()
        screen.addstr(10, 50, "LOADING..", curses.col["green-black"])
        screen.addstr(11, 50, "████████      ]50% ", curses.col["green-black"])
        screen.refresh()
        time.sleep(1)
        screen.addstr(11, 50, "██████████████]99% ", curses.col["green-black"])
        screen.refresh()
        time.sleep(0.5)
        screen.addstr(11, 50, "█████████████ ]98% ", curses.col["green-black"])
        screen.refresh()
        time.sleep(0.5)
        screen.addstr(11, 50, "██████████████]99% ", curses.col["green-black"])
        screen.refresh()
        
        run(self.game)
        if not self.game.solved:
            self.game.saveGame()
        quit()

    

    def loadGame(self):
        try:
            continuedSudoku = SudokuReader('continue_pickle', rand = False).extract()
            originalSudoku = SudokuReader('continue_pickle', rand = False).extract(index = 1)
            os.remove("continue_pickle")
            self.game = SudokuGame(continuedSudoku,2,2, original_sud = originalSudoku)
            self.goGame()
        except Exception:
            screen.clear()
            screen.addstr(10, 60, "There is no sudoku to continue")
            screen.nodelay(False)
            event = screen.getch()
            if event == 10:
                screen.clear()
                self.startMenu()
                return


    def quitApp(self):
        self.STOP = True
        Quit()

    def getHelp(self):
        screen.clear()
        instructions = ["To start a new game, go back and choose \"New game\"",
                    "To continue last game, go back and choose \"Continue last game\"",
                    "To move around the board, use arrow keys",
                    "To place emoji at cursor, press enter",
                    "To delete emoji at cursor, press backspac",
                    "To check if your solution is correct, press spacebar",
                    "To quit the game or camera window, press \"q\" in the focused window"]
        screen.addstr(5, 40, "How to play the game", curses.col["yellow-black"] | curses.A_BOLD | curses.A_UNDERLINE)
        c = 0
        for i in instructions:
            screen.addstr(8+c, 20, i)
            c+= 1

        screen.addstr(20, 40, "How to play 4x4 sudoku", curses.col["yellow-black"] | curses.A_BOLD | curses.A_UNDERLINE)
        screen.addstr(23, 20, "Every row, column and mini-grid must contain four different emojis.")
        screen.addstr(24, 20, "Fill out the missing emojis.")

        screen.nodelay(False)
        event = screen.getch()
        screen.clear()
        self.startMenu()
        
            
            


    def addOptions(self):
        count = 0
        for option in self.options:
            screen.addstr(self.init_y + count, self.init_x, option.name, curses.col["cyan-black"])
            count += 1
        

    def startMenu(self):
        self.addOptions()
        self.moveCursor()

       



def run(board):
    cam = CamDetection()

    ''' The thread that deals with the sudoku game'''
    def sudPart():
        while True:
            screen.clear()
            doUpdate = board.update(arg = cam.result+1)
            if doUpdate == False:    
                Quit()  
                break
            screen.nodelay(True)
            event = screen.getch()
            if event == ord("e"): # Shouldn't be necessary, but is there in case someone gets stuck here
                Quit()
                
        

    ''' The thread that deals with the emotion detection'''
    def camPart():
        while True:
            cam.thefunction()
            result = cam.result
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


    ''' Threading the sudoku game and the camera together'''
    def startGame(thread1, thread2):
        t2 = threading.Thread(target=thread1) 
        t1 = threading.Thread(target=thread2)     
        t1.start(); t2.start()
        t1.join();  t2.join() 


    startGame(sudPart, camPart)
    cam.cap.release()
    cv2.destroyWindow('video')


def gogo():
    initializeCurses()
    menu = Menu(5,2)
    cv2.destroyAllWindows()
    curses.endwin()
    quit()

gogo()

#run()


"""
''' Loading the sudoku pickle file '''
filename = 'sudoku_pickle'
infile = open(filename,'rb')
sudoku_list = pickle.load(infile)
infile.close()
#print(sudoku_list[0])
"""