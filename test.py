from sklearn.neighbors import KNeighborsClassifier

import cv2
import pickle
import json
import numpy as np
import os

video = cv2.VideoCapture(0)     # 0 - for built in camera(laptops)  1 - for external cameras(pcs)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

with open('names.pkl', 'rb') as f:
    LABELS = pickle.load(f)
    
with open('faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)


knn = KNeighborsClassifier(n_neighbors = 5)
knn.fit(FACES,LABELS)


while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3 ,5)
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50,50)).flatten().reshape(1,-1)
        output = knn.predict(resized_img)
        cv2.putText(frame, str(output[0]), (x,y-15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
        cv2.rectangle(frame, (x,y), (x+w, y+h), (50, 50, 255), 1)
    cv2.imshow("Frame", frame)
    k = cv2.waitKey(1)
    if k==ord('q'):     # NOTE you change from 100 to 10
        break

video.release()
cv2.destroyAllWindows()





# THE FUCKING FAT NOTE FOR YOU FAT FUCK (even though u have underweght): YOU HAVE STOPPED AT 32:13 OF https://www.youtube.com/watch?v=BYCKvM8eZGA DO NOT FUCKING FORGET TO CHANGE THE 0 TO 1 OR WHATEVERT YK THE CAMERA BULLSHIT
# THOSE ERRORS ARE FALSE POSITIVES 