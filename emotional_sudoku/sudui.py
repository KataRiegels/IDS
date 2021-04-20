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
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    curses.curs_set(1)
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

    def numAsEmoji(self):
        return convertToEmoji(self.getNumber())


    def printNumber(self):
        '''Print the number'''
        if self.getState() == 1:
            screen.addstr("%s " % convertToEmoji(self.getNumber()), curses.color_pair(4))
        elif self.getState() == 0:
            screen.addstr("%s " % convertToEmoji(self.getNumber()), curses.color_pair(1))		



class Cursor:
    '''
    An object to move the cursor with rules 
    Usage: MoveCursor(initial x position, initial y position, move left jump size, move right jump size, go up jump size, go down jump size, up limit size, down limit size, left limit size, right limit size) 
    '''
    def __init__(self, init_x, init_y):
        self.x = init_x
        self.y = init_y


    def move(self):
        screen.move(self.y,self.x)
        
 



def Quit():
    '''Quiiiiiiiit!!!'''
    curses.endwin()
    #quit()

class Board():
    '''The game board'''
    def __init__(self,sudoku_size,init_x, init_y):
        self.Board = [[N(0)]*sudoku_size for i in range(sudoku_size)]
        self.sudsize = sudoku_size


class GameBoard(Board):
    '''The game board'''
    def __init__(self, size, init_x, init_y, horjump = 3, verjump = 1):
        Board.__init__(self, size, init_x, init_y)
        #board = Board(self, size, init_x, init_y, horjump, verjump)
        self.current_row = 0
        self.current_column = 0
        #self.init_cursor_x, self.init_cursor_y = init_x + horjump, init_y + verjump

        self.init_x = init_x
        self.init_y = init_y
        self.sudoku_size = size
        self.xjump = horjump
        self.yjump = verjump
        


        self.current_row = 0
        self.current_column = 0
        self.cursor = Cursor(self.init_x, self.init_y)
        self.cursor.x, self.cursor.y = 0,0
        
        self.printcolor = curses.color_pair(2)
        self.bar_color  = curses.color_pair(6)
        self.input_color = curses.color_pair(3)
        self.moveCursor()
    
    



    def Print(self):
        '''Method to print our game board'''
        hor_square_bars = "  " + "-" * ((self.sudoku_size+self.sudSqrt()) * 3 - 1)
        ver_bar = self.printfield("|")
        extraY = 1

        screen.addstr(self.init_y, self.init_x, hor_square_bars, self.bar_color) 

        for y in range(self.sudoku_size): 
            if ((y+1) % self.sudSqrt() == 1) and (y+1 > self.sudSqrt()):
                screen.addstr(self.init_y+y+extraY, self.init_x, hor_square_bars, self.bar_color)
                extraY += 1
            
            screen.addstr(self.init_y+y+extraY, self.init_x, ver_bar, self.bar_color)
            for x in range(self.sudoku_size):
                if ((x+1) % self.sudSqrt() == 1) and (x+1 > self.sudSqrt()):
                    screen.addstr(ver_bar, self.bar_color)
                if self.Board[x][y].getNumber() != 0:
                    screen.addstr(self.printfield(self.Board[x][y].numAsEmoji()), self.input_color)
                else:
                    screen.addstr(self.printfield(" "))
            screen.addstr(ver_bar, self.bar_color)
        screen.addstr(self.init_y + self.sudoku_size + extraY, self.init_x, hor_square_bars, self.bar_color) 
        



    def matrixToInner(self, current_x, current_y, jumpx = 3, jumpy = 1):
        outer_x = current_x + math.floor(current_x/math.sqrt(self.sudoku_size))
        outer_y = current_y + math.floor(current_y/math.sqrt(self.sudoku_size))
        inner_x = jumpx * outer_x + self.init_x + (jumpx + 1) #+ math.ceil(jumpx/2)) #length + length / 2
        inner_y = jumpy * outer_y + self.init_y + (jumpy) # + math.ceil(jumpy/2))
        return [inner_x, inner_y]

    def moveCursor(self):
        pos = self.matrixToInner(self.current_column, self.current_row)
        self.cursor.x, self.cursor.y = pos[0],pos[1]
        self.cursor.move()
        

    def update(self, arg):
        '''Method where we read the keyboard keys and think in the game :P'''
        if True:
            screen.nodelay(True)
            self.moveCursor()

            self.Print()
            self.moveCursor()
            number = arg
            
            screen.addstr(10, 10 , f'Emoji to enter: {N(number).numAsEmoji()}')
            self.moveCursor()
            self.Print()
            self.moveCursor()
            event = screen.getch()
            if event == ord("w"): 
                Quit()
                quit()
                return
            elif event == (curses.KEY_LEFT):
                self.current_column -= 1
                if self.current_column < 0:
                    self.current_column = 3
            elif event == curses.KEY_RIGHT:
                self.current_column += 1
                if self.current_column > 3:
                    self.current_column = 0
            elif event == curses.KEY_UP:
                self.current_row -= 1
                if self.current_row < 0:
                    self.current_row = 3
            elif event == curses.KEY_DOWN:
                self.current_row += 1
                if self.current_row > 3:
                    self.current_row = 0
            elif event == 10:
                screen.nodelay(False)
                self.Board[self.current_column][self.current_row] = N(number)
                self.Print()
            self.moveCursor()
            


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

    def Play(self,x,y, number):
        '''The play method :)'''
        self.setNumber(x,y,number,False)
  








if sys.platform == 'linux':
    from gpiozero import CPUTemperature


class CamDetection():
        


    # dictionary which assigns each label an emotion (alphabetical order)

    def __init__(self):
        self.result = 4

        # input arg parsing
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--fullscreen',
                            help='Display window in full screen', action='store_true')
        parser.add_argument(
            '-d', '--debug', help='Display debug info', action='store_true')
        parser.add_argument(
            '-fl', '--flip', help='Flip incoming video signal', action='store_true')
        self.args = parser.parse_args()

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
        self.model = model
        # prevents openCL usage and unnecessary logging messages
        cv2.ocl.setUseOpenCL(False)
        self.emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful",
                        3: "Horny", 4: "Neutral", 5: "Sad", 6: "Surprised"}
        self.cap = cv2.VideoCapture(0)
        self.counter = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

    def get_gpu_temp(self):
        temp = subprocess.check_output(['vcgencmd measure_temp | egrep -o \'[0-9]*\.[0-9]*\''],
                                        shell=True, universal_newlines=True)
        return str(float(temp))

    def above10(self,dic:dict, lastreturn):
        result = lastreturn
        for i in dic:
            if dic[i] > 10:
                return i
                for i in dic:
                    dic[i] = 0
        return result


    def thefunction(self):
        #finalresult = 4


        # time for fps
        start_time = time.time()

        # Find haar cascade to draw bounding box around face
        ret, frame = self.cap.read()
        if self.args.flip:
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
            prediction = self.model.predict(cropped_img)
            #print(prediction)
            maxindex = int(np.argmax(prediction))
            self.counter[maxindex] += 1
            cv2.putText(frame, self.emotion_dict[maxindex], (x+20, y-60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        print(f'counter: {self.counter}')
        # full screen
        if self.args.fullscreen:
            cv2.namedWindow("video", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("video", cv2.WND_PROP_FULLSCREEN, 1)

        # debug info
        if self.args.debug:
            fps = str(int(1.0 / (time.time() - start_time)))
            cv2.putText(frame, fps + " fps", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            if sys.platform == 'linux':
                cpu_temp = str(int(CPUTemperature().temperature)) + " C (CPU)"
                cv2.putText(frame, cpu_temp, (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                cv2.putText(frame, get_gpu_temp() + " C (GPU)", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow('video', cv2.resize(
            frame, (800, 480), interpolation=cv2.INTER_CUBIC))
        #result = above10(counter, result)
        #dic = self.counter
        for i in self.counter:
            if self.counter[i] >= 10:
                self.result = i
                print(self.result)
                #self.counter = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
                print(f'emo dict: {self.emotion_dict[self.result]}')
                for i in self.counter:
                    self.counter[i] = 0
        #if result != 4:
            #finalresult = result



InitCurses()
cam = CamDetection()

board = GameBoard(4, 2, 2)
result = None

def sudPart():
    while True:
        try:
            #result = in_q.get()
            screen.clear()
            
            #print(f'sudpart result: {cam.result}')
            
            board.update(arg = cam.result)
            screen.nodelay(True)
            event = screen.getch()
            if event == ord("w"): 
                Quit()
                quit()
        except:
            print("SUDPART BROKE")
            break
        #screen.nodelay(False)
    
    

#def camPart(out_q):
def camPart():

    while True:
        try:
            cam.thefunction()
            result = cam.result
            #if result != None:
            #out_q.put(result)
            #print(f'result: {result}')
            #print(f'out_q: {out_q}')
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except:
            print("cat part BroKE")
            break


try:
    #q = Queue()
    #t2 = threading.Thread(target=sudPart, args = (q, )) 
    #t1 = threading.Thread(target=camPart, args = (q, ))     # function is used as argument
    t2 = threading.Thread(target=sudPart) 
    t1 = threading.Thread(target=camPart)     # function is used as argument

    t1.start()
    t2.start()


    #q.join()
    t2.join() 
    t1.join()
except:
    print("didnt work") 
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
cam.cap.release()
cv2.destroyAllWindows()



