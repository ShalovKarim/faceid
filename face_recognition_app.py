"""
Face Recognition App
====================
Recognizes faces via webcam, displays names, and logs detection counts to database.json.

Requirements:
    pip install face_recognition opencv-python numpy

Usage:
    python face_recognition_app.py
    Press 'q' to quit.
"""

import cv2
import face_recognition
import json
import os
import numpy as np
from datetime import datetime

# ── Paths ────────────────────────────────────────────────────────────────────
KNOWN_FACES_DIR = "known_faces"   # Folder with sub-folders named after each person
DATABASE_FILE   = "database.json" # JSON database for detection counts

# ── Helpers ──────────────────────────────────────────────────────────────────

def load_database() -> dict:
    """Load the JSON database. Creates it if it doesn't exist."""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_database(db: dict) -> None:
    """Persist the database back to disk."""
    with open(DATABASE_FILE, "w") as f:
        json.dump(db, f, indent=4)
    print(f"[DB] Saved → {DATABASE_FILE}")


def increment_detection(db: dict, name: str) -> dict:
    """
    Increment the detection count for `name` in the database.
    Each person entry looks like:
        {
            "detections": 42,
            "last_seen": "2026-04-15 10:23:01"
        }
    """
    if name not in db:
        db[name] = {"detections": 0, "last_seen": None}

    db[name]["detections"] += 1
    db[name]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return db


def load_known_faces(directory: str):
    """
    Walk `directory` for sub-folders named after people.
    Each image inside is encoded and stored.

    Structure:
        known_faces/
            Alice/
                alice1.jpg
                alice2.jpg
            Bob/
                bob.png
    """
    known_encodings = []
    known_names     = []

    if not os.path.isdir(directory):
        print(f"[WARN] '{directory}' not found. Run register_faces.py first.")
        return known_encodings, known_names

    for person_name in os.listdir(directory):
        person_path = os.path.join(directory, person_name)
        if not os.path.isdir(person_path):
            continue

        loaded = 0
        for filename in os.listdir(person_path):
            if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                continue

            img_path = os.path.join(person_path, filename)
            image    = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(person_name)
                loaded += 1
            else:
                print(f"[WARN] No face found in {img_path} — skipping.")

        print(f"[LOAD] {person_name}: {loaded} image(s) loaded.")

    return known_encodings, known_names


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  Face Recognition App")
    print("  Press 'q' to quit | 's' to force-save DB")
    print("=" * 50)

    # Load known faces
    known_encodings, known_names = load_known_faces(KNOWN_FACES_DIR)
    print(f"\n[INFO] {len(set(known_names))} person(s) registered.\n")

    # Load JSON database
    db = load_database()

    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam. Check your camera index.")
        return

    # Track who was detected in the current "session window" to avoid
    # spamming the counter every single frame.
    last_logged: dict[str, float] = {}  # name → timestamp (seconds)
    LOG_COOLDOWN = 5.0  # seconds between DB increments for the same person

    frame_skip = 0  # Process every other frame for speed

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read frame.")
            break

        frame_skip += 1
        if frame_skip % 2 != 0:
            # Still show the frame, just skip recognition
            cv2.imshow("Face Recognition  |  q=quit  s=save", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # Resize for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small   = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations  = face_recognition.face_locations(rgb_small)
        face_encodings  = face_recognition.face_encodings(rgb_small, face_locations)

        now = datetime.now().timestamp()

        for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
            name       = "Unknown"
            color      = (0, 0, 220)  # Red for unknown
            confidence = None

            if known_encodings:
                distances = face_recognition.face_distance(known_encodings, encoding)
                best_idx  = int(np.argmin(distances))
                best_dist = distances[best_idx]

                if best_dist < 0.55:  # Threshold — lower = stricter
                    name       = known_names[best_idx]
                    color      = (50, 200, 50)  # Green for known
                    confidence = round((1 - best_dist) * 100, 1)

                    # Update DB with cooldown
                    elapsed = now - last_logged.get(name, 0)
                    if elapsed >= LOG_COOLDOWN:
                        db = increment_detection(db, name)
                        save_database(db)
                        last_logged[name] = now
                        print(f"[DB]  {name} → detections={db[name]['detections']}")

            # Scale coordinates back to full frame size
            top    *= 2; right  *= 2
            bottom *= 2; left   *= 2

            # Draw bounding box
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            # Label background
            label = f"{name}  {confidence}%" if confidence else name
            label_y = top - 10 if top > 30 else bottom + 25
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_DUPLEX, 0.65, 1)
            cv2.rectangle(frame, (left, label_y - th - 6), (left + tw + 8, label_y + 4), color, -1)
            cv2.putText(frame, label, (left + 4, label_y),
                        cv2.FONT_HERSHEY_DUPLEX, 0.65, (255, 255, 255), 1)

            # Show detection count from DB
            if name != "Unknown" and name in db:
                count_label = f"Seen: {db[name]['detections']}x"
                cv2.putText(frame, count_label, (left + 4, bottom + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        cv2.imshow("Face Recognition  |  q=quit  s=save", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            save_database(db)

    # Cleanup
    save_database(db)
    cap.release()
    cv2.destroyAllWindows()
    print("\n[INFO] Session ended. Database saved.")


if __name__ == "__main__":
    main()
