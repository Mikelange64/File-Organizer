#!/usr/bin/env python3
"""File Organizer & Duplicate Finder

Usage: python organizer.py <command> [args]

Commands: organize, duplicates, rename, find-large, cleanup, tree, undo
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "config.json"
OPS_LOG = ROOT / "operations.json"


def load_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {"categories": {}, "ignore": []}


def human_size(n):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024.0:
            return f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}PB"


def parse_size(s):
    s = s.strip().upper()
    mult = 1
    if s.endswith("KB"):
        mult = 1024
        s = s[:-2]
    elif s.endswith("MB"):
        mult = 1024 ** 2
        s = s[:-2]
    elif s.endswith("GB"):
        mult = 1024 ** 3
        s = s[:-2]
    elif s.endswith("B"):
        s = s[:-1]
    try:
        return int(float(s) * mult)
    except Exception:
        raise argparse.ArgumentTypeError("Invalid size")


def ensure_dir(p):
    p.mkdir(parents=True, exist_ok=True)


def move_file_safe(src: Path, dest: Path, dry_run=False):
    ensure_dir(dest.parent)
    target = dest
    i = 1
    while target.exists():
        stem = dest.stem
        suffix = dest.suffix
        target = dest.with_name(f"{stem}_{i}{suffix}")
        i += 1
    if dry_run:
        return str(target)
    shutil.move(str(src), str(target))
    return str(target)


def hash_file(path: Path, algo="sha256"):
    h = hashlib.new(algo)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def log_op(op):
    data = []
    if OPS_LOG.exists():
        try:
            data = json.loads(OPS_LOG.read_text())
        except Exception:
            data = []
    data.append(op)
    OPS_LOG.write_text(json.dumps(data, indent=2))


def undo_last():
    if not OPS_LOG.exists():
        print("No operations to undo.")
        return
    data = json.loads(OPS_LOG.read_text())
    if not data:
        print("No operations to undo.")
        return
    op = data.pop()
    OPS_LOG.write_text(json.dumps(data, indent=2))
    kind = op.get("action")
    if kind == "move":
        src = Path(op["from"])  # where it was moved from originally
        dst = Path(op["to"])    # current location
        if dst.exists():
            ensure_dir(src.parent)
            shutil.move(str(dst), str(src))
            print(f"Moved back {dst} -> {src}")
        else:
            print("Target file for undo not found:", dst)
    elif kind == "delete":
        print("Cannot undo permanent delete via this log.")
    else:
        print("Unknown operation to undo.")


def cmd_organize(args):
    cfg = load_config()
    categories = {k: set(v) for k, v in cfg.get("categories", {}).items()}
    ignore = set(cfg.get("ignore", []))
    root = Path(args.path).expanduser()
    if not root.exists():
        print("Path does not exist")
        return
    print(f"📂 Organizing {root}...")
    counts = {k: 0 for k in categories}
    counts["Others"] = 0
    total = 0
    started = datetime.now()
    for p in root.iterdir():
        if p.name in ignore or p.is_dir():
            continue
        ext = p.suffix.lower()
        placed = False
        for cat, exts in categories.items():
            if ext in exts:
                dest = root / cat / p.name
                dest_str = move_file_safe(p, dest, dry_run=args.dry_run)
                if not args.dry_run:
                    log_op({"action": "move", "from": str(p), "to": dest_str, "ts": datetime.now().isoformat()})
                counts[cat] += 1
                placed = True
                total += 1
                break
        if not placed:
            dest = root / "Others" / p.name
            dest_str = move_file_safe(p, dest, dry_run=args.dry_run)
            if not args.dry_run:
                log_op({"action": "move", "from": str(p), "to": dest_str, "ts": datetime.now().isoformat()})
            counts["Others"] += 1
            total += 1
    elapsed = (datetime.now() - started).total_seconds()
    print("\nCreated folders:")
    for k, v in counts.items():
        if v:
            emoji = {
                "Images": "📷",
                "Documents": "📄",
                "Audio": "🎵",
                "Videos": "🎬",
                "Archives": "📦",
                "Others": "❓",
            }.get(k, "📁")
            print(f"  {emoji} {k}/     ({v} files)")
    print(f"\n✅ Organized {total} files in {elapsed:.2f} seconds")


def cmd_duplicates(args):
    root = Path(args.path).expanduser()
    if not root.exists():
        print("Path does not exist")
        return
    print(f"Scanning {root} for duplicates...")
    hashes = {}
    for p in root.rglob("*"):
        if p.is_file():
            try:
                h = hash_file(p)
            except PermissionError:
                continue
            hashes.setdefault(h, []).append(p)
    groups = [v for v in hashes.values() if len(v) > 1]
    wasted = 0
    for group in groups:
        size = sum(p.stat().st_size for p in group[1:])
        wasted += size
        print("\nDuplicate group:")
        for p in group:
            print(" ", p)
        print("Group size:", human_size(sum(p.stat().st_size for p in group)), " wasted:", human_size(size))
        if args.remove:
            keep = group[0]
            to_delete = group[1:]
            print(f"Keeping: {keep}")
            for p in to_delete:
                if args.dry_run:
                    print("Would delete", p)
                else:
                    p.unlink()
                    log_op({"action": "delete", "path": str(p), "ts": datetime.now().isoformat()})
                    print("Deleted", p)
    print(f"\nFound {len(groups)} duplicate groups. Potential wasted space: {human_size(wasted)}")


def cmd_rename(args):
    root = Path(args.path).expanduser()
    files = [p for p in root.iterdir() if p.is_file()]
    if args.pattern:
        cnt = 1
        preview = []
        for p in files:
            new_name = args.pattern.replace("{count}", str(cnt))
            if "{orig}" in new_name:
                new_name = new_name.replace("{orig}", p.stem)
            if not Path(new_name).suffix:
                new_name = f"{new_name}{p.suffix}"
            dest = p.with_name(new_name)
            preview.append((p, dest))
            cnt += 1
        if args.preview:
            for a, b in preview:
                print(a, "->", b)
            return
        for a, b in preview:
            if args.dry_run:
                print("Would rename", a, "->", b)
            else:
                a.rename(b)
                log_op({"action": "move", "from": str(a), "to": str(b), "ts": datetime.now().isoformat()})
                print(a, "->", b)
        return
    # prefix/suffix/date
    for p in files:
        name = p.stem
        if args.add_prefix:
            name = f"{args.add_prefix}{name}"
        if args.add_suffix:
            name = f"{name}{args.add_suffix}"
        if args.add_date:
            name = f"{datetime.now().strftime('%Y%m%d')}_{name}"
        dest = p.with_name(name + p.suffix)
        if args.preview:
            print(p, "->", dest)
        else:
            if args.dry_run:
                print("Would rename", p, "->", dest)
            else:
                p.rename(dest)
                log_op({"action": "move", "from": str(p), "to": str(dest), "ts": datetime.now().isoformat()})
                print(p, "->", dest)


def cmd_find_large(args):
    root = Path(args.path).expanduser()
    if not root.exists():
        print("Path does not exist")
        return
    min_bytes = args.min_size
    files = [p for p in root.rglob("*") if p.is_file() and p.stat().st_size >= min_bytes]
    files.sort(key=lambda p: p.stat().st_size, reverse=True)
    total = 0
    for p in files:
        sz = p.stat().st_size
        total += sz
        print(human_size(sz), p)
    print("\nTotal:", human_size(total))


def cmd_cleanup(args):
    root = Path(args.path).expanduser()
    if not root.exists():
        print("Path does not exist")
        return
    if args.older_than:
        cutoff = datetime.now(timezone.utc) - timedelta(days=args.older_than)
        removed = 0
        size = 0
        for p in root.rglob("*"):
            if p.is_file():
                mtime = datetime.fromtimestamp(p.stat().st_mtime, timezone.utc)
                if mtime < cutoff:
                    if args.dry_run:
                        print("Would delete", p)
                    else:
                        size += p.stat().st_size
                        p.unlink()
                        log_op({"action": "delete", "path": str(p), "ts": datetime.now().isoformat()})
                        removed += 1
        print(f"Removed {removed} files, freed {human_size(size)}")
    if args.empty_folders:
        removed = 0
        for d in sorted([p for p in root.rglob("*") if p.is_dir()], key=lambda x: len(str(x)), reverse=True):
            try:
                if not any(d.iterdir()):
                    if args.dry_run:
                        print("Would remove empty folder", d)
                    else:
                        d.rmdir()
                        removed += 1
            except PermissionError:
                continue
        print(f"Removed {removed} empty folders")


def cmd_tree(args):
    root = Path(args.path).expanduser()
    if not root.exists():
        print("Path does not exist")
        return
    def walk(p, depth, prefix=""):
        if depth < 0:
            return
        items = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        for i, item in enumerate(items):
            connector = "└─" if i == len(items)-1 else "├─"
            if item.is_dir():
                print(prefix + connector + item.name + "/")
                walk(item, depth-1, prefix + ("   " if i==len(items)-1 else "│  "))
            else:
                print(prefix + connector + item.name + " (" + human_size(item.stat().st_size) + ")")
    walk(root, args.depth)


def main():
    parser = argparse.ArgumentParser(prog="organizer.py")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("organize")
    p.add_argument("path")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_organize)

    p = sub.add_parser("duplicates")
    p.add_argument("path")
    p.add_argument("--remove", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_duplicates)

    p = sub.add_parser("rename")
    p.add_argument("path")
    p.add_argument("--pattern", help='Use {count} and {orig}')
    p.add_argument("--add-prefix")
    p.add_argument("--add-suffix")
    p.add_argument("--add-date", action="store_true")
    p.add_argument("--preview", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_rename)

    p = sub.add_parser("find-large")
    p.add_argument("path")
    p.add_argument("--min-size", type=parse_size, default=parse_size("100MB"))
    p.set_defaults(func=cmd_find_large)

    p = sub.add_parser("cleanup")
    p.add_argument("path")
    p.add_argument("--older-than", type=int)
    p.add_argument("--empty-folders", dest="empty_folders", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_cleanup)

    p = sub.add_parser("tree")
    p.add_argument("path")
    p.add_argument("--depth", type=int, default=2)
    p.set_defaults(func=cmd_tree)

    p = sub.add_parser("undo")
    p.set_defaults(func=lambda args: undo_last())

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
