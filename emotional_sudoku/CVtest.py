import cv2
import numpy as np
import tensorflow as tf
import tensorflow.keras

#load our model
model1 = tensorflow.keras.models.load_model('keras_model.h5')
emojimodel = tensorflow.keras.models.load_model('emoji_model.h5')
#initialize an array tocontain frame information
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
emojidata = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)


#load our label dictionary
label_dict = {0: "Thumbs up", 1: "Background", 2: "Thumbs Down",
                3: "Blood"}
emoji_dict = {0: "grimace", 1: "wow", 2:"tongue out", 3:"kissy", 4: "null"}


#start webcam
cam = cv2.VideoCapture(0)
while True:
    font = cv2.FONT_HERSHEY_SIMPLEX
    retval, frame = cam.read()
    frame = cv2.flip(frame, 1)
    #break the loop if nothing is being captured
    if not retval:
        break

    # Draw a rectangle, in the frame
    thumbFrame = cv2.rectangle(frame, (420, 200), (790, 470), (0, 0, 255), 3)
    emojiframe = cv2.rectangle(frame, (32,32), (300,400), (255, 0, 0), 3)
    # Draw another rectangle in which the image to labelled is to be shown.
    frame2 = thumbFrame[200:470, 420:790]
    frame3 = emojiframe[32:400, 32:300]
    # resizing the image to be at least 224x224 and then cropping from the center
    frame2 = cv2.resize(frame2, (224, 224))
    frame3 = cv2.resize(frame3, (224,224))
    # turn the image into a numpy array
    image_array = np.asarray(frame2)
    image_array2 = np.asarray(frame3)
    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    normalized_image_array2 = (image_array.astype(np.float32)/ 127.0) - 1
    # Load the image into the array
    data[0] = normalized_image_array
    emojidata[0]= normalized_image_array2

    pred = model1.predict(data)
    emoji = emojimodel.predict(emojidata)

    result = np.argmax(pred[0])
    emojiresult = np.argmax(emoji[0])

    cv2.putText(frame, label_dict[int(result)], (420, 220), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, emoji_dict[emojiresult], (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    #show webcam feed
    cv2.imshow('video', cv2.resize(
        frame, (800, 480), interpolation=None))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


