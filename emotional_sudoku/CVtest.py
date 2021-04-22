from cv2 import cv2
import numpy as np
import tensorflow as tf
import tensorflow.keras

#load our model
model1 = tensorflow.keras.models.load_model('keras_model.h5')
emojimodel = tensorflow.keras.models.load_model('emotions.h5')
#initialize an array tocontain frame information
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
emojidata = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)


#load our label dictionary
label_dict = {0: "Thumbs up", 1: "Background", 2: "Thumbs Down",
                3: "Blood"}
emoji_dict = {0: "grimace", 1: "wow", 2:"tongue out", 3:"kissy"}


#start webcam
cam = cv2.VideoCapture(1)
facecasc = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
font = cv2.FONT_HERSHEY_SIMPLEX
count = 0
while True:
    retval, frame = cam.read()
    frame = cv2.flip(frame, 1)
    #break the loop if nothing is being captured
    if not retval:
        break

    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facecasc.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    for(x, y, w, h) in faces:
        emojiframe = cv2.rectangle(frame, (x-10, y-50), (x+w+10, y+h+30), (255, 0, 0), 2)
        frame3 = frame[y-50:y + h + 10, x-10:x + w +10]
        frame3 = cv2.resize(frame3, (224, 224))
        image_array2 = np.asarray(frame3)
        emojidata[0]=(image_array2.astype(np.float32) / 127.0) - 1
        emoji = emojimodel.predict(emojidata)
        print(emoji)
        count += 1
        print(count)
        emojiresult = np.argmax(emoji[0])
        cv2.putText(frame, emoji_dict[int(emojiresult)], (10, 25), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
    # Draw a rectangle, in the frame
    thumbFrame = cv2.rectangle(frame, (420, 200), (790, 470), (0, 0, 255), 3)
    ##emojiframe = cv2.rectangle(frame, (1,1), (799,479), (255, 0, 0), 3)
    # Draw another rectangle in which the image to labelled is to be shown.
    frame2 = thumbFrame[200:470, 420:790]
    ##frame3 = emojiframe[1:479, 1:799]
    # resizing the image to be at least 224x224 and then cropping from the center
    frame2 = cv2.resize(frame2, (224, 224))
    
    # turn the image into a numpy array
    image_array = np.asarray(frame2)
    
    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    # normalized_image_array2 = (image_array2.astype(np.float32)/ 127.0) - 1
    # Load the image into the array
    data[0] = normalized_image_array
    # emojidata[0]= image_array2.astype(np.float32)  #normalized_image_array2
    

    pred = model1.predict(data)

    #print(pred)
   

    result = np.argmax(pred[0])

    cv2.putText(frame, label_dict[int(result)], (420, 220), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

    #show webcam feed
    cv2.imshow('video', cv2.resize(
        frame, (800, 480), interpolation=None))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


