import json
import pickle
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

JSONType = Union[Dict[str, Any], List[Any], str, int, float, bool, None]


class StorageBackend:
    """Base storage backend interface."""

    def load(self) -> Dict[str, Any]:
        raise NotImplementedError

    def save(self) -> None:
        raise NotImplementedError

    def set(self, key: str, value: Any) -> None:
        raise NotImplementedError

    def get(self, key: str, default: Any = None) -> Any:
        raise NotImplementedError

    def delete(self, key: str) -> None:
        raise NotImplementedError

    def all(self) -> Dict[str, Any]:
        raise NotImplementedError


class JsonStorage(StorageBackend):
    """JSON file storage backend."""

    def __init__(self, path: Union[str, Path], default: Optional[Dict[str, Any]] = None):
        self.path = Path(path)
        self.default = default if default is not None else {}
        self.data = self.load()

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.data = self.default.copy()
            self.save()
            return self.data

        try:
            with self.path.open("r", encoding="utf-8") as f:
                value = json.load(f)
            return value if isinstance(value, dict) else {}
        except json.JSONDecodeError:
            return {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        self.save()

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def delete(self, key: str) -> None:
        self.data.pop(key, None)
        self.save()

    def all(self) -> Dict[str, Any]:
        return self.data.copy()


class SqliteStorage(StorageBackend):
    """SQLite storage backend for key/value JSON data."""

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path))
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS storage (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        self.conn.commit()

    def _serialize(self, value: Any) -> str:
        return json.dumps(value, ensure_ascii=False)

    def _deserialize(self, value: str) -> Any:
        return json.loads(value)

    def load(self) -> Dict[str, Any]:
        cursor = self.conn.execute("SELECT key, value FROM storage")
        return {key: self._deserialize(value) for key, value in cursor.fetchall()}

    def save(self) -> None:
        self.conn.commit()

    def set(self, key: str, value: Any) -> None:
        serialized = self._serialize(value)
        self.conn.execute(
            "INSERT INTO storage (key, value) VALUES (?, ?)"
            " ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, serialized),
        )
        self.save()

    def get(self, key: str, default: Any = None) -> Any:
        cursor = self.conn.execute("SELECT value FROM storage WHERE key = ?", (key,))
        row = cursor.fetchone()
        return self._deserialize(row[0]) if row else default

    def delete(self, key: str) -> None:
        self.conn.execute("DELETE FROM storage WHERE key = ?", (key,))
        self.save()

    def all(self) -> Dict[str, Any]:
        return self.load()

    def close(self) -> None:
        self.conn.close()


class PickleStorage(StorageBackend):
    """Pickle storage backend for key/value data."""

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self.load()

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {}

        try:
            with self.path.open("rb") as f:
                value = pickle.load(f)
            return value if isinstance(value, dict) else {}
        except Exception:
            return {}

    def save(self) -> None:
        with self.path.open("wb") as f:
            pickle.dump(self.data, f)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        self.save()

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def delete(self, key: str) -> None:
        self.data.pop(key, None)
        self.save()

    def all(self) -> Dict[str, Any]:
        return self.data.copy()


def create_json_file(path: Union[str, Path], default: Optional[Dict[str, Any]] = None) -> Path:
    path = Path(path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json(path, default if default is not None else {})
    return path


def write_json(path: Union[str, Path], data: Any, indent: int = 4) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def read_json(path: Union[str, Path]) -> Optional[Any]:
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


def get_storage(backend: str, path: Union[str, Path], default: Optional[Dict[str, Any]] = None) -> StorageBackend:
    backend = backend.lower()
    if backend == "json":
        return JsonStorage(path, default=default)
    if backend == "sqlite":
        return SqliteStorage(path)
    if backend == "pickle":
        return PickleStorage(path)
    raise ValueError(f"Unknown backend: {backend}. Use 'json', 'sqlite', or 'pickle'.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Simple dynamic storage utility")
    parser.add_argument("backend", choices=["json", "sqlite", "pickle"], nargs="?", default="json", help="Storage backend to use")
    parser.add_argument("path", nargs="?", default="sample_data.json", help="Path to storage file")
    args = parser.parse_args()

    storage = get_storage(args.backend, args.path, default={})
    storage.set("name", "Alice")
    storage.set("age", 30)
    storage.set("skills", ["python", "json", "sqlite"])

    print(f"Using backend: {args.backend}")
    print("Saved data:", storage.all())
    print("Loaded data:", storage.load())

    if isinstance(storage, SqliteStorage):
        storage.close()
