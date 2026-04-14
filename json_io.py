import json
from pathlib import Path


def create_json_file(path, default=None):
    """Create a JSON file if it does not exist.

    Args:
        path (str | Path): The file path to create.
        default (Any): Initial value to write if the file is created.
    Returns:
        Path: The file path.
    """
    path = Path(path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json(path, default if default is not None else {})
    return path


def write_json(path, data, indent=4):
    """Write Python data to a JSON file.

    Args:
        path (str | Path): The file path to write.
        data (Any): The Python object to serialize.
        indent (int): JSON indentation level.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def read_json(path):
    """Read JSON data from a file.

    Args:
        path (str | Path): The file path to read.
    Returns:
        Any: The Python object loaded from JSON, or None if not readable.
    """
    path = Path(path)
    if not path.exists():
        print(f"File does not exist: {path}")
        return None

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Failed to decode JSON from {path}: {exc}")
        return None


if __name__ == "__main__":
    sample_path = "sample_data.json"
    sample_data = {
        "name": "Alice",
        "age": 30,
        "skills": ["python", "json", "file io"]
    }

    create_json_file(sample_path, default={})
    write_json(sample_path, sample_data)
    print(f"Wrote sample JSON to {sample_path}")

    loaded = read_json(sample_path)
    print("Loaded JSON:", loaded)
