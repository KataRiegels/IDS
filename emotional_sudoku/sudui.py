import argparse
import os
import sys
import time
import threading
from queue import Queue
import copy

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import cv2
import numpy as np
from tensorflow.keras.layers import (Conv2D, Dense, Dropout, Flatten,
                                     MaxPooling2D)
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D

import subprocess
import math
import curses
import random
from random import shuffle
from past.builtins import (str as oldstr, range, reduce,
                               raw_input, xrange)
screen = curses.initscr()

board_size = 9
board_startPos = 3,3

def convertToEmoji(number):
    if number == 1:
        return ":)"
    if number == 2:
        return ":("
    if number == 3:
        return ":o"
    else:
        return ":*"


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



class N:
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
            screen.addstr("%s " % convertToEmoji(self.getNumber()), curses.color_pair(4))
        elif self.getState() == 0:
            screen.addstr("%s " % convertToEmoji(self.getNumber()), curses.color_pair(1))		



class MoveCursor:
    '''
    An object to move the cursor with rules 
    Usage: MoveCursor(initial x position, initial y position, move left jump size, move right jump size, go up jump size, go down jump size, up limit size, down limit size, left limit size, right limit size) 
    '''
    board_size = 24
    
    jumplen_hor = 1
    jumplen_ver = 1



    def __init__(self, init_x, init_y, lines_to_skip = None, lines_to_skip_input = None):
        self.x = init_x
        self.y = init_y
        self.leftbound = init_x
        self.rightbound = init_x + (self.jumplen_hor * self.board_size) -1
        self.upperbound = init_y
        self.lowerbound = init_y + (self.jumplen_ver * self.board_size) +  int(math.sqrt(board_size)) -2


    def MoveActual(self):
        screen.move(self.y,self.x)
        
    def Move(self,option):
        
        if option == 'actual':
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
    #quit()

class Board():
    '''The game board'''
    def __init__(self,sudoku_size,init_x, init_y, horjump = 3, verjump = 1):
        lists = [N(0)]*sudoku_size
        #Number(0),Number(0),Number(0),Number(0),Number(0),Number(0),Number(0),Number(0),Number(0)
        self.Board = [[N(0)]*sudoku_size for i in range(sudoku_size)]
        #self.Board = [[Number(0)]*sudoku_size]*sudoku_size # create the Board
        self.sudsize = sudoku_size
        self.horizontal_jump = horjump   # How much it jumps in x direction

        #self.Board_x = x # lines
        #self.Board_y = y # columns
        #for i in range(0,sudoku_size): # create the Board columns
         #   self.Board.append([])



class GameBoard(Board):
    '''The game board'''
    def __init__(self, size, init_x, init_y, horjump = 3, verjump = 1):
        Board.__init__(self, size, init_x, init_y, horjump, verjump)
        #board = Board(self, size, init_x, init_y, horjump, verjump)
        self.current_row = 0
        self.current_column = 0
        #self.init_cursor_x, self.init_cursor_y = init_x + horjump, init_y + verjump

        self.init_x = init_x
        self.init_y = init_y
        self.sudoku_size = size
        self.xjump = horjump
        self.yjump = verjump
        self.noof_inner_lines = int(math.sqrt(board_size)) - 1   # The amount of vertical lines inside the sudoku (e.g. 4x4 has 1)
        self.xdim = (2 + self.noof_inner_lines + self.sudoku_size) * self.xjump # 2 -> outer vertical lines. 
        self.ydim = (2 + self.noof_inner_lines + self.sudoku_size) * self.yjump
        


        self.current_row = 0
        self.current_column = 0
        self.cursor = MoveCursor(init_x, init_y)
        init_cursor = self.matrixToInner(0,0)
        self.cursor.x, self.cursor.y = init_cursor[0], init_cursor[1]
        self.cursor.Move('actual')
        self.board_left = init_x 
        self.board_right = self.board_left + (size + self.noof_inner_lines) * self.xjump
        self.upperbound = init_y
        self.lowerbound = self.upperbound + board_size + self.noof_inner_lines

        self.printcolor = curses.color_pair(2)

        #self.Number = Number(0)
        #self.Fill()
    
    



    def Print(self):
        '''Method to print our game board'''
        ver_square_bars = "-" * self.xdim
        listofprints = []
        lineprint = ""
        pos = None
        screen.addstr(self.init_y, self.init_x, ver_square_bars, curses.color_pair(5)) 

        for y in range(self.sudoku_size): 
            if ((y+1) % self.sudSqrt() == 1) and (y+1 > self.sudSqrt()):
                #screen.addstr(self.init_y + y, self.init_x, ver_square_bars)
                lineprint = ver_square_bars
                listofprints.append(lineprint)
            lineprint = self.printfield("|")
            for x in range(self.sudoku_size):
                if ((x+1) % self.sudSqrt() == 1) and (x+1 > self.sudSqrt()):
                    lineprint += self.printfield("|")
                if self.Board[x][y].getNumber() != 0:
                    inp = self.printfield(self.Board[x][y].getNumber())
                else:
                    inp = " "
                lineprint += self.printfield(inp)
            lineprint += self.printfield("|")
            listofprints.append(lineprint)
        listofprints.append(ver_square_bars)
        count = 0
        for q in listofprints:
            screen.addstr(count + self.init_y+1, self.init_x , q)
            count += 1  
           # screen.addstr(count + self.init_y+1, self.init_x , "kælkælkæk")
        #if pos:
         #   for i in pos: 
          #      screen.addstr(i[0], i[1], self.printfield(self.Board[x][y].getNumber()), self.printcolor)






    def matrixToInner(self, current_x, current_y, jumpx = 3, jumpy = 1):
        outer_x = current_x + math.floor(current_x/math.sqrt(self.sudoku_size))
        outer_y = current_y + math.floor(current_y/math.sqrt(self.sudoku_size))
        """
        screen.addstr(20, 50,str(f'current_x: {current_x}'))
        screen.addstr(21, 50, str(f'current_y: {current_y}'))
        
        screen.addstr(22, 50,str(f'outer_x: {outer_x}'))
        screen.addstr(23, 50, str(f'outer_y: {outer_y}'))


        screen.addstr(24, 50,str(f'math floor_x: {math.floor(current_x/self.sudoku_size)}'))
        screen.addstr(25, 50, str(f'math floor_y: {math.floor(current_y/self.sudoku_size)}'))
        """


        inner_x = jumpx * outer_x + self.init_x + (jumpx + 1) #+ math.ceil(jumpx/2)) #length + length / 2
        inner_y = jumpy * outer_y + self.init_y + (jumpy) # + math.ceil(jumpy/2))
        return [inner_x, inner_y]

    def moveCursor(self):
        pos = self.matrixToInner(self.current_column, self.current_row)
        self.cursor.x, self.cursor.y = pos[0],pos[1]
        self.cursor.Move('actual')
        

    def update(self, arg):
        '''Method where we read the keyboard keys and think in the game :P'''
        list = [ ] # create a list with numbers from 9 to 1. We will get the index from the event. example: 57-49=8, but the 8 number is the number 1 so we reverse the list so the index is correct :)
        for i in range (1,10):
            list.append(i)
        list.reverse()
        print(f'board up: {arg}')
        starty = 50
        startx = 20
        while True:
            screen.nodelay(False)
            #screen.clear()
            self.Print()
            self.cursor.Move('actual')
            number = arg
            if number:
                self.Board[self.current_column][self.current_row] = N(number)
            self.Print()
            self.printcolor = curses.color_pair(2)
            event = screen.getch()
            if event == ord("w"): 
                Quit()
                return
            elif event == (curses.KEY_LEFT or "w"):
                self.current_column -= 1
            elif event == curses.KEY_RIGHT:
                self.current_column += 1
            elif event == curses.KEY_UP:
                self.current_row -= 1
            elif event == curses.KEY_DOWN:
                self.current_row += 1
            elif event == curses.KEY_ENTER:
                #screen.nodelay(False)
                self.Print()
                notEnter = True
                while notEnter:
                    number = arg
                    self.Board[self.current_column][self.current_row] = N(number)
                    #self.cursor.Move('actual')
                    
                    self.Print()
                    key = screen.getch()
                    if key == 10:
                        notEnter = False
                    #    screen.nodelay(True)
            #elif event >= 
            """
            elif event >= 48 and event <= 57: # from 1 to 9
                number = event-48
                self.Print()
                notEnter = True
                while notEnter:
                    self.Board[self.current_column][self.current_row] = N(number)
                    #self.cursor.Move('actual')
                    
                    self.Print()
                    self.moveCursor()
                    multiplier = 10
                    key = screen.getch()
                    if key == 10:
                        self.printcolor = curses.color_pair(0)
                        notEnter = False
                    
                    elif key >= 48 and key <= 57:
                        number = (number)*multiplier + key-48
                        multiplier *= 10
                self.Board[self.current_column][self.current_row] = N(number)
            """
            self.moveCursor()
            


    def asciiToInt(self, ascii_):
        return ascii_-48

    def sudSqrt(self):
        return int(math.sqrt(self.sudoku_size))


    def printfield(self, inp):
        inp = str(inp)
        left  = " " * ( + int((self.xjump- len(str(inp)))/2))
        right = " " * (self.xjump - len(left) - len(str(inp)))
        return left + inp + right

    def Fill(self):
        '''Fill the board with random numbers so we can create random Sudoku'''
        for x in range(0,self.sudoku_size): # first we fill the board with 0's
            for y in range(0,self.sudoku_size):
                self.Board[x].append(N(0))

    def setNumber(self, x, y, number, state):
        '''Set the desired number and lock it if True'''
        self.Board[x][y] = N(number)
        #if state:
         #   self.Board[x][y].setLock()

    def Play(self,x,y, number):
        '''The play method :)'''
        #if self.Board[x][y].getNumber() == 0:
        self.setNumber(x,y,number,False)
  




"""
if __name__ == '__main__': 

    InitCurses()
    run_for_your_life = Menu() # The menu
    curses.napms(3000)
    curses.endwin()
"""




if sys.platform == 'linux':
    from gpiozero import CPUTemperature

# input arg parsing
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fullscreen',
                    help='Display window in full screen', action='store_true')
parser.add_argument(
    '-d', '--debug', help='Display debug info', action='store_true')
parser.add_argument(
    '-fl', '--flip', help='Flip incoming video signal', action='store_true')
args = parser.parse_args()

# create model (convolutional nn)
model = Sequential()

model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48, 48, 1)))
model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(1024, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(7, activation='softmax'))

model.load_weights('model.h5')

# prevents openCL usage and unnecessary logging messages
cv2.ocl.setUseOpenCL(False)

# dictionary which assigns each label an emotion (alphabetical order)
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful",
                3: "Horny", 4: "Neutral", 5: "Sad", 6: "Surprised"}

def get_gpu_temp():
    temp = subprocess.check_output(['vcgencmd measure_temp | egrep -o \'[0-9]*\.[0-9]*\''],
                                    shell=True, universal_newlines=True)
    return str(float(temp))

def above10(dic:dict):
    for i in dic:
        if dic[i] > 10:
            dic[i] = 0
            return i
    return 4


# start the webcam feed
cap = cv2.VideoCapture(0)
counter = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
#finalresult = 1
def thefunction(counter):
    #finalresult = 4


    # time for fps
    start_time = time.time()

    # Find haar cascade to draw bounding box around face
    ret, frame = cap.read()
    if args.flip:
        frame = cv2.flip(frame, 0)
    if not ret:
        return
    facecasc = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facecasc.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0)
        prediction = model.predict(cropped_img)
        #print(prediction)
        maxindex = int(np.argmax(prediction))
        counter[maxindex] += 1
        cv2.putText(frame, emotion_dict[maxindex], (x+20, y-60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    print(f'counter: {counter}')
    # full screen
    if args.fullscreen:
        cv2.namedWindow("video", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("video", cv2.WND_PROP_FULLSCREEN, 1)

    # debug info
    if args.debug:
        fps = str(int(1.0 / (time.time() - start_time)))
        cv2.putText(frame, fps + " fps", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        if sys.platform == 'linux':
            cpu_temp = str(int(CPUTemperature().temperature)) + " C (CPU)"
            cv2.putText(frame, cpu_temp, (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, get_gpu_temp() + " C (GPU)", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.imshow('video', cv2.resize(
        frame, (800, 480), interpolation=cv2.INTER_CUBIC))
    result = above10(counter)
    if result != 4:
        #finalresult = result
        counter = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        print(f'emo dict: {emotion_dict[result]}')

    return result

InitCurses()

board = GameBoard(4, 2, 2)
result = None
def sudPart(in_q):
    while True:
        result = in_q.get()
        screen.clear()
        
        print(f'sudpart result: {result}')
        
        board.update(arg = result)
        screen.nodelay(True)
        event = screen.getch()
        if event == ord("w"): 
            Quit()
            quit()
        #screen.nodelay(False)
    
    

def camPart(out_q):
    while True:
        result = thefunction(counter)
        if result != None:
            out_q.put(result)
        #print(f'result: {result}')
        #print(f'out_q: {out_q}')
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

q = Queue()
t2 = threading.Thread(target=sudPart, args = (q, )) 
t1 = threading.Thread(target=camPart, args = (q, ))     # function is used as argument

t1.start()
t2.start()


#q.join()
t2.join() 
t1.join() 
"""
while True:
    result = thefunction(counter)
    #if result != None:
     #   out_q.put(result)
    print(f'result: {result}')
    #print(f'out_q: {out_q}')
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
"""

"""
while True:
    

    screen.clear()

    #board.update()
    #emotion = thefunction(counter)
    
    
    event = screen.getch()
    if event == ord("w"): 
        Quit()
        quit()
"""    
curses.napms(3000)
curses.endwin()
cap.release()
cv2.destroyAllWindows()



