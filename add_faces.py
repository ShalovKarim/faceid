import cv2
import pickle
import numpy as np
import os

video = cv2.VideoCapture(1)     # 0 - for built in camera(laptops)  1 - for external cameras(pcs)
facedetect = cv2.CascadeClassifier('faceid\data\haarcascade_frontalface_default.xml')

face_data = []
i=0

name = input("Enter Your Name you fat fuhh: ")


while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3 ,5)
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50,50))
        if len(face_data) <= 100 and i%10 == 0:
            face_data.append(resized_img)
        i=i+1
        cv2.putText(frame, str(len(face_data)), (50,50), cv2.FONT_HERSHEY_COMPLEX, 1, (50,50,255), 1)
        cv2.rectangle(frame, (x,y), (x+w, y+h), (50, 50, 255), 1)
    cv2.imshow("Frame", frame)
    k = cv2.waitKey(1)
    if k==ord('q') or len(face_data) == 100:
        break

video.release()
cv2.destroyAllWindows()

face_data = np.asarray(face_data)
face_data = face_data.reshape(100,-1)



if 'names.pkl' not in os.listdir('faceid/data/'):
    names = [name] * 100
    with open('faceid/names.pkl', 'wb') as f:
        pickle.dump(names, f)
else:
    with open('faceid/names.pkl', 'rb') as f:
        names = pickle.load(f)
    names = names + [name]*100
    with open('faceid/names.pkl', 'wb') as f:
        pickle.dump(names, f)


        
if 'faces_data.pkl' not in os.listdir('faceid/data/'):
    with open('faceid/faces_data.pkl', "wb") as f:
        pickle.dump(face_data, f)
else:
    with open('faceid/faces_data.pkl', 'rb') as f:
        faces = pickle.load(f)
    faces = np.append(faces, face_data, axis= 0)
    with open('faceid/faces_data.pkl', 'wb') as f:
        pickle.dump(faces, f)



# THE FUCKING FAT NOTE FOR YOU FAT FUCK (even though u have underweght): YOU HAVE STOPPED AT 27:23 OF https://www.youtube.com/watch?v=BYCKvM8eZGA DO NOT FUCKING FORGET TO CHANGE THE 0 TO 1 OR WHATEVERT YK THE CAMERA BULLSHIT