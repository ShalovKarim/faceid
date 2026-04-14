import json

FILE = "batteries.json"

def write_data(class_name, count):
    try:
        with open(FILE, "r") as f:
            data = json.load(f)
    except:
        data = {}

    data[class_name] = count

    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

    print("data saved")
def read_data():
    try:
        with open(FILE, "r") as f:
            data = json.load(f)
    except:
        print("file is not exist or empty")
        return

    print("results:")
    for class_name, count in data.items():
        print(class_name, "→", count)
