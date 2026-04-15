# 🎭 Face Recognition App

Recognizes faces from your webcam and logs detection counts into a local `database.json`.

---

## 📁 File Structure

```
face_recognition_app/
├── face_recognition_app.py   ← Main app (run this)
├── register_faces.py         ← Register new people
├── db_manager.py             ← View/edit the database
├── database.json             ← Your JSON database (auto-managed)
└── known_faces/              ← Face image storage (auto-created)
    ├── Alice/
    │   ├── Alice_1.jpg
    │   └── Alice_2.jpg
    └── Bob/
        └── Bob_1.jpg
```

---

## ⚙️ Installation

```bash
pip install face_recognition opencv-python numpy
```

> **Note:** `face_recognition` requires `cmake` and `dlib`.
> - **macOS:** `brew install cmake`
> - **Ubuntu/Debian:** `sudo apt install build-essential cmake`
> - **Windows:** Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) first.

---

## 🚀 Quickstart

### Step 1 — Register a face from webcam
```bash
python register_faces.py register --name "Alice" --capture 5
```
Press **SPACE** to capture each photo. Capture 5–10 photos for best accuracy.

### Step 2 — Register from an existing image
```bash
python register_faces.py register --name "Bob" --image /path/to/bob.jpg
```

### Step 3 — Run the app
```bash
python face_recognition_app.py
```
- Press **Q** to quit
- Press **S** to force-save the database

---

## 🗄️ JSON Database (`database.json`)

The database is automatically updated while the app is running.

```json
{
    "Alice": {
        "detections": 42,
        "last_seen": "2026-04-15 10:23:01"
    },
    "Bob": {
        "detections": 7,
        "last_seen": "2026-04-14 18:55:12"
    }
}
```

- **`detections`** — integer count incremented each time the face is seen (with a 5-second cooldown per person to avoid spamming)
- **`last_seen`** — timestamp of the most recent detection

---

## 🛠️ Database Manager (`db_manager.py`)

```bash
# Show all entries with a visual bar chart
python db_manager.py show

# Reset one person's count
python db_manager.py reset --name "Alice"

# Reset everyone
python db_manager.py reset --all

# Manually set a count
python db_manager.py set --name "Bob" --detections 10

# Export to CSV
python db_manager.py export --format csv
```

---

## 📋 Register Faces CLI

```bash
# List all registered people + stats
python register_faces.py list

# Remove a person entirely
python register_faces.py remove --name "Alice"
```

---

## 🎛️ Tuning

In `face_recognition_app.py`, you can adjust:

| Setting | Default | Description |
|---------|---------|-------------|
| `LOG_COOLDOWN` | `5.0` sec | Seconds between DB increments per person |
| Threshold `0.55` | `0.55` | Lower = stricter matching (try 0.45–0.6) |
| `fx=0.5` resize | `0.5` | Lower = faster but less accurate |

---

## 💡 Tips

- Use **5–10 photos** per person for best accuracy.
- Vary angles slightly when capturing (left, right, straight).
- Good lighting dramatically improves recognition.
- The app processes **every other frame** for performance — increase `frame_skip` modulo for weaker hardware.
