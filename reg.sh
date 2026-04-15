echo please enter your name 

read -p 'Enter your name: ' username

python3 register_faces.py --name $username --capture 5

python3 face_recognition_app.py