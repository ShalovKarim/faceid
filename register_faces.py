"""
Register Faces
==============
Use this script to add new people to the face recognition system.

Two modes:
  1. Capture from webcam  →  python register_faces.py --name "Alice" --capture 5
  2. Import existing image →  python register_faces.py --name "Alice" --image path/to/photo.jpg

Requirements:
    pip install face_recognition opencv-python numpy
"""

import cv2
import face_recognition
import argparse
import os
import shutil
import json

KNOWN_FACES_DIR = "known_faces"
DATABASE_FILE   = "database.json"


def ensure_person_dir(name: str) -> str:
    path = os.path.join(KNOWN_FACES_DIR, name)
    os.makedirs(path, exist_ok=True)
    return path


def load_database() -> dict:
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_database(db: dict) -> None:
    with open(DATABASE_FILE, "w") as f:
        json.dump(db, f, indent=4)


def register_from_image(name: str, image_path: str) -> None:
    """Copy an existing image into the known_faces directory after validating it has a face."""
    if not os.path.isfile(image_path):
        print(f"[ERROR] File not found: {image_path}")
        return

    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)

    if not encodings:
        print(f"[ERROR] No face detected in '{image_path}'. Please use a clear frontal photo.")
        return

    person_dir = ensure_person_dir(name)
    ext        = os.path.splitext(image_path)[1]
    existing   = len(os.listdir(person_dir))
    dest       = os.path.join(person_dir, f"{name}_{existing + 1}{ext}")
    shutil.copy2(image_path, dest)
    print(f"[OK] Registered '{name}' from image → {dest}")

    # Add to database if not present
    db = load_database()
    if name not in db:
        db[name] = {"detections": 0, "last_seen": None}
        save_database(db)
        print(f"[DB] Added '{name}' to database.")
    else:
        print(f"[DB] '{name}' already exists in database (detections: {db[name]['detections']}).")


def register_from_webcam(name: str, num_photos: int = 5) -> None:
    """Capture `num_photos` photos from the webcam for a person."""
    person_dir = ensure_person_dir(name)
    cap        = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        return

    print(f"\n[INFO] Capturing {num_photos} photos for '{name}'.")
    print("       Position your face clearly in the frame.")
    print("       Press SPACE to capture | Q to quit early.\n")

    captured   = 0
    existing   = len([f for f in os.listdir(person_dir) if f.lower().endswith((".jpg",".jpeg",".png"))])

    while captured < num_photos:
        ret, frame = cap.read()
        if not ret:
            break

        # Show guide overlay
        display = frame.copy()
        cv2.putText(display,
                    f"Capturing '{name}': {captured}/{num_photos}  [SPACE=capture  Q=quit]",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Live face detection guide box
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locs = face_recognition.face_locations(rgb)
        for (top, right, bottom, left) in locs:
            cv2.rectangle(display, (left, top), (right, bottom), (0, 200, 255), 2)

        cv2.imshow("Register Face", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            # Validate face presence
            encodings = face_recognition.face_encodings(rgb, locs)
            if not encodings:
                print("[WARN] No face detected — try again.")
                continue

            filename = os.path.join(person_dir, f"{name}_{existing + captured + 1}.jpg")
            cv2.imwrite(filename, frame)
            captured += 1
            print(f"  [{captured}/{num_photos}] Saved → {filename}")

        elif key == ord('q'):
            print("[INFO] Quit early.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if captured > 0:
        print(f"\n[OK] Registered {captured} photo(s) for '{name}'.")
        db = load_database()
        if name not in db:
            db[name] = {"detections": 0, "last_seen": None}
            save_database(db)
            print(f"[DB] Added '{name}' to database.")
        else:
            print(f"[DB] '{name}' already in database.")
    else:
        print("[WARN] No photos captured.")


def list_registered() -> None:
    """Print all registered people and their database stats."""
    db = load_database()

    if not os.path.isdir(KNOWN_FACES_DIR):
        print("[INFO] No known_faces directory found.")
        return

    people = [d for d in os.listdir(KNOWN_FACES_DIR)
              if os.path.isdir(os.path.join(KNOWN_FACES_DIR, d))]

    if not people:
        print("[INFO] No faces registered yet.")
        return

    print(f"\n{'Name':<20} {'Photos':<10} {'Detections':<12} {'Last Seen'}")
    print("-" * 60)
    for person in sorted(people):
        person_dir = os.path.join(KNOWN_FACES_DIR, person)
        photos     = len([f for f in os.listdir(person_dir)
                          if f.lower().endswith((".jpg",".jpeg",".png",".bmp"))])
        stats      = db.get(person, {})
        detections = stats.get("detections", 0)
        last_seen  = stats.get("last_seen", "Never")
        print(f"{person:<20} {photos:<10} {detections:<12} {last_seen}")


def remove_person(name: str) -> None:
    """Remove a person from known_faces and the database."""
    person_dir = os.path.join(KNOWN_FACES_DIR, name)
    if os.path.isdir(person_dir):
        shutil.rmtree(person_dir)
        print(f"[OK] Removed face data for '{name}'.")
    else:
        print(f"[WARN] No face directory found for '{name}'.")

    db = load_database()
    if name in db:
        del db[name]
        save_database(db)
        print(f"[DB] Removed '{name}' from database.")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Register faces for the recognition app.")
    sub    = parser.add_subparsers(dest="command")

    # register --name "Alice" --capture 5
    reg = sub.add_parser("register", help="Register a new person")
    reg.add_argument("--name",    required=True, help="Person's name")
    reg.add_argument("--capture", type=int, default=0,
                     help="Capture N photos from webcam (default: 0)")
    reg.add_argument("--image",   default=None,
                     help="Path to an existing image file")

    # list
    sub.add_parser("list", help="List all registered people")

    # remove --name "Alice"
    rem = sub.add_parser("remove", help="Remove a person")
    rem.add_argument("--name", required=True, help="Person's name to remove")

    args = parser.parse_args()

    if args.command == "register":
        if args.image:
            register_from_image(args.name, args.image)
        elif args.capture > 0:
            register_from_webcam(args.name, args.capture)
        else:
            print("[ERROR] Provide --image <path> or --capture <N>")

    elif args.command == "list":
        list_registered()

    elif args.command == "remove":
        remove_person(args.name)

    else:
        parser.print_help()
