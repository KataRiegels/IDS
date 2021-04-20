import argparse
import os
import sys

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import cv2
import numpy as np

import time
from tensorflow.keras.layers import (Conv2D, Dense, Dropout, Flatten, MaxPooling2D)
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D

import subprocess
import math
import curses

import threading




screen = curses.initscr()

board_size = 9

def Quit():
    curses.endwin()


def initializeCurses():
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

    # Converts the numbers into matching emojis
    def convertToEmoji(self,number):
        if number == 0:
            return "DELETE"
        if number == 1:
            return ":)"
        if number == 2:
            return ":("
        if number == 3:
            return ":o"
        else:
            return ":*"

    # Lock number (or opposite)
    def setLock(self):
        if self.state == 0:
            self.state = 1
        else:
            self.state = 0	

    # Locked or not
    def getState(self):
        return self.state
        
    # Return the actual int
    def getNumber(self):
        return self.suit

    # Returns the number converted to emoji
    def numAsEmoji(self):
        return self.convertToEmoji(self.getNumber())


'''  The sudoku game, which contains a board to print and the update function  '''
class SudokuGame():
    def __init__(self, size, init_x, init_y, horjump = 3, verjump = 1):
        self.board = [[N(0)]*size for i in range(size)]
        self.sudoku_size = size

        self.init_x,         self.init_y      = init_x,  init_y
        self.xjump,          self.yjump       = horjump, verjump
        self.current_column, self.current_row = 0,       0
        
        self.bar_color  = curses.color_pair(6)
        self.input_color = curses.color_pair(3)
        self.moveCursor()


    ''' Prints the board as it currently is.''' 
    def Print(self):
        hor_square_bars = "  " + "-" * ((self.sudoku_size+self.sudSqrt()) * self.xjump - 1)
        ver_bar = self.printfield("|")
        extraY = 1
        
        
        screen.addstr(self.init_y, self.init_x, hor_square_bars, self.bar_color)        # prints the upper line
        # prints everything on the board as well as the vertical bars and inner horizontal lines
        for y in range(self.sudoku_size):
            # Checking whether there needs to be a horizontal line
            if ((y+1) % self.sudSqrt() == 1) and (y+1 > self.sudSqrt()):
                screen.addstr(self.init_y+y+extraY, self.init_x, hor_square_bars, self.bar_color)
                extraY += 1
            screen.addstr(self.init_y+y+extraY, self.init_x, ver_bar, self.bar_color)   # Left-most bar

            for x in range(self.sudoku_size):
                # Checks when to draw bar
                if ((x+1) % self.sudSqrt() == 1) and (x+1 > self.sudSqrt()):
                    screen.addstr(ver_bar, self.bar_color)
                # Print either the emoji or whitespaces if cell has not been filled
                if self.board[x][y].getNumber() != 0:
                    screen.addstr(self.printfield(self.board[x][y].numAsEmoji()), self.input_color)
                else:
                    screen.addstr(self.printfield(" "))
            screen.addstr(ver_bar, self.bar_color)                                       # right-most bar
        screen.addstr(self.init_y + self.sudoku_size + extraY, self.init_x, hor_square_bars, self.bar_color) # lower line
        


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
    def update(self, arg):
        
        screen.clear()
        screen.nodelay(True)
        self.moveCursor()
        
        screen.addstr((self.sudoku_size+self.sudSqrt() * self.xjump ) , 5 , f'Press enter to insert Emoji: ', curses.color_pair(1))
        screen.addstr(N(arg).numAsEmoji(), curses.color_pair(5))
        self.Print()
        self.moveCursor()
        event = screen.getch()
        if event == ord("w"): 
            Quit()
            quit()
            return
        elif event == curses.KEY_LEFT:
            self.current_column -= 1
            if self.current_column < 0:
                self.current_column = self.sudoku_size -1
        elif event == curses.KEY_RIGHT:
            self.current_column += 1
            if self.current_column > self.sudoku_size -1:
                self.current_column = 0
        elif event == curses.KEY_UP:
            self.current_row -= 1
            if self.current_row < 0:
                self.current_row = self.sudoku_size -1
        elif event == curses.KEY_DOWN:
            self.current_row += 1
            if self.current_row > self.sudoku_size -1:
                self.current_row = 0
        elif event == 10:
            screen.nodelay(False)
            self.board[self.current_column][self.current_row] = N(arg)
            self.Print()
        self.moveCursor()
            

    # Simply returns the square root of the size
    def sudSqrt(self):
        return int(math.sqrt(self.sudoku_size))

    # Makes sure the input for a cell will stay somewhat in the middle. Flexible on cell-size
    def printfield(self, inp):
        inp = str(inp)
        left  = " " * ( + int((self.xjump- len(str(inp)))/2))
        right = " " * (self.xjump - len(left) - len(str(inp)))
        return left + inp + right






if sys.platform == 'linux':
    from gpiozero import CPUTemperature


class CamDetection():
        
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
        for i in self.counter:
            if self.counter[i] >= 10:
                self.result = i
                print(self.result)
                print(f'emo dict: {self.emotion_dict[self.result]}')
                for i in self.counter:
                    self.counter[i] = 0



initializeCurses()
cam = CamDetection()

board = SudokuGame(board_size, 2, 2)

''' The thread that deals with the sudoku game'''
def sudPart():
    while True:
        screen.clear()
        board.update(arg = cam.result)
        screen.nodelay(True)
        event = screen.getch()
        if event == ord("w"): 
            Quit()
            quit()
    

''' The thread that deals with the emotion detecction'''
def camPart():
    while True:
        cam.thefunction()
        result = cam.result
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


''' Threading the soduko game and the camera together'''
t2 = threading.Thread(target=sudPart) 
t1 = threading.Thread(target=camPart)     
t1.start(); t2.start()
t1.join();  t2.join() 

# Make sure everything is closed
curses.endwin()
cam.cap.release()
cv2.destroyAllWindows()



