echo please enter your name

set /p username="Type your name here: "

python register_faces.py --name %username% --capture 5

python face_recognition_app.py