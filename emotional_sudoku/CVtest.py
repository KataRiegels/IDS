import cv2
import numpy as np
import tensorflow as tf
import tensorflow.keras

#load our model
model = tensorflow.keras.models.load_model('keras_model.h5')

#initialize an array tocontain frame information
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)


#load our label dictionary
label_dict = {0: "Thumbs up", 1: "Background", 2: "Thumbs Down",
                3: "Blood"}

#start webcam
cam = cv2.VideoCapture(0)
while True:
    font = cv2.FONT_HERSHEY_SIMPLEX
    retval, frame = cam.read()
    #break the loop if nothing is being captured
    if not retval:
        break
    facecasc = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facecasc.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (255, 0, 0), 2)

    # Draw a rectangle, in the frame
    frame = cv2.rectangle(frame, (420, 200), (790, 470), (0, 0, 255), 3)
    # Draw another rectangle in which the image to labelled is to be shown.
    frame2 = frame[200:470, 420:790]
    # resizing the image to be at least 224x224 and then cropping from the center
    frame2 = cv2.resize(frame2, (224, 224))
    # turn the image into a numpy array
    image_array = np.asarray(frame2)
    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    # Load the image into the array
    data[0] = normalized_image_array
    pred = model.predict(data)
    result = np.argmax(pred[0])
    cv2.putText(frame, label_dict[int(result)], (420, 220), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

    #show webcam feed
    cv2.imshow('video', cv2.resize(
        frame, (800, 480), interpolation=cv2.INTER_CUBIC))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


