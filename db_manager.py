"""
Database Manager
================
View, edit, reset, or export your face recognition JSON database.

Usage:
    python db_manager.py show
    python db_manager.py reset --name "Alice"
    python db_manager.py reset --all
    python db_manager.py set --name "Alice" --detections 10
    python db_manager.py export --format csv
"""

import json
import os
import argparse
import csv

DATABASE_FILE = "database.json"


def load() -> dict:
    if not os.path.exists(DATABASE_FILE):
        print(f"[ERROR] {DATABASE_FILE} not found.")
        exit(1)
    with open(DATABASE_FILE) as f:
        return json.load(f)


def save(db: dict) -> None:
    with open(DATABASE_FILE, "w") as f:
        json.dump(db, f, indent=4)
    print(f"[OK] Saved {DATABASE_FILE}")


def show(db: dict) -> None:
    if not db:
        print("[INFO] Database is empty.")
        return

    print(f"\n  {'Name':<22} {'Detections':>12}   Last Seen")
    print("  " + "─" * 58)
    total = 0
    for name, stats in sorted(db.items()):
        d  = stats.get("detections", 0)
        ls = stats.get("last_seen") or "Never"
        total += d
        bar = "█" * min(d, 30)
        print(f"  {name:<22} {d:>8}x   {ls}   {bar}")
    print("  " + "─" * 58)
    print(f"  {'TOTAL':<22} {total:>8}x\n")


def reset_person(db: dict, name: str) -> dict:
    if name not in db:
        print(f"[WARN] '{name}' not found in database.")
        return db
    db[name]["detections"] = 0
    db[name]["last_seen"]  = None
    print(f"[OK] Reset '{name}'.")
    return db


def set_detections(db: dict, name: str, value: int) -> dict:
    if name not in db:
        db[name] = {"detections": 0, "last_seen": None}
    db[name]["detections"] = value
    print(f"[OK] Set '{name}' detections → {value}")
    return db


def export_csv(db: dict) -> None:
    outfile = "database_export.csv"
    with open(outfile, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "detections", "last_seen"])
        writer.writeheader()
        for name, stats in sorted(db.items()):
            writer.writerow({
                "name":       name,
                "detections": stats.get("detections", 0),
                "last_seen":  stats.get("last_seen") or ""
            })
    print(f"[OK] Exported → {outfile}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage face recognition database.")
    sub    = parser.add_subparsers(dest="command")

    sub.add_parser("show", help="Display all entries")

    res = sub.add_parser("reset", help="Reset detection count(s)")
    res.add_argument("--name", help="Person name to reset")
    res.add_argument("--all",  action="store_true", help="Reset everyone")

    sett = sub.add_parser("set", help="Manually set detection count")
    sett.add_argument("--name",       required=True)
    sett.add_argument("--detections", type=int, required=True)

    exp = sub.add_parser("export", help="Export database")
    exp.add_argument("--format", choices=["csv", "json"], default="csv")

    args = parser.parse_args()
    db   = load()

    if args.command == "show":
        show(db)

    elif args.command == "reset":
        if args.all:
            for name in db:
                db = reset_person(db, name)
            save(db)
        elif args.name:
            db = reset_person(db, args.name)
            save(db)
        else:
            print("[ERROR] Provide --name or --all")

    elif args.command == "set":
        db = set_detections(db, args.name, args.detections)
        save(db)

    elif args.command == "export":
        if args.format == "csv":
            export_csv(db)
        else:
            print(json.dumps(db, indent=4))

    else:
        parser.print_help()
