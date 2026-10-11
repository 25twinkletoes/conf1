from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Dict, Optional


@dataclass
class Node:
    name: str
    is_dir: bool
    content: str = ""
    children: Dict[str, "Node"] = field(default_factory=dict)


class VFS:
    """In-memory virtual file system loaded from a real directory."""

    def __init__(self, source: str | Path):
        self.source = Path(source).expanduser().resolve()
        if not self.source.exists():
            raise FileNotFoundError(f"VFS source does not exist: {self.source}")
        if not self.source.is_dir():
            raise NotADirectoryError(f"VFS source is not a directory: {self.source}")
        self.root = Node("/", True)
        self.cwd = PurePosixPath("/")
        self._load()

    def _load(self):
        for item in self.source.rglob("*"):
            rel = item.relative_to(self.source).as_posix()
            parts = rel.split("/")
            cur = self.root
            for i, part in enumerate(parts):
                last = i == len(parts) - 1
                if part not in cur.children:
                    cur.children[part] = Node(part, item.is_dir() if last else True)
                cur = cur.children[part]
                if last and item.is_file():
                    try:
                        cur.content = item.read_text(encoding="utf-8")
                    except UnicodeDecodeError:
                        cur.content = item.read_text(encoding="utf-8", errors="replace")

    def _normalize(self, path: str | None) -> PurePosixPath:
        if path is None or path == "":
            return self.cwd
        p = PurePosixPath(path)
        if not p.is_absolute():
            p = self.cwd / p
        parts = []
        for part in p.parts:
            if part in ("", "."):
                continue
            if part == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(part)
        return PurePosixPath("/") / PurePosixPath(*parts)

    def resolve(self, path: str | None = None) -> Node:
        p = self._normalize(path)
        cur = self.root
        for part in p.parts:
            if part == "/":
                continue
            if part not in cur.children:
                raise FileNotFoundError(f"No such file or directory: {p}")
            cur = cur.children[part]
        return cur

    def exists(self, path: str) -> bool:
        try:
            self.resolve(path)
            return True
        except FileNotFoundError:
            return False

    def is_dir(self, path: str) -> bool:
        return self.resolve(path).is_dir

    def list_dir(self, path: str | None = None) -> list[str]:
        node = self.resolve(path)
        if not node.is_dir:
            raise NotADirectoryError(f"Not a directory: {path}")
        return sorted(node.children)

    def change_dir(self, path: str):
        node = self.resolve(path)
        if not node.is_dir:
            raise NotADirectoryError(f"Not a directory: {path}")
        self.cwd = self._normalize(path)

    def read_file(self, path: str) -> str:
        node = self.resolve(path)
        if node.is_dir:
            raise IsADirectoryError(f"Is a directory: {path}")
        return node.content

    def touch(self, path: str):
        p = self._normalize(path)
        if p == PurePosixPath("/"):
            raise ValueError("cannot touch root")
        parent = self.resolve(str(p.parent))
        if not parent.is_dir:
            raise NotADirectoryError(str(p.parent))
        name = p.name
        if name not in parent.children:
            parent.children[name] = Node(name, False)

    def mkdir(self, path: str):
        p = self._normalize(path)
        if p == PurePosixPath("/"):
            raise FileExistsError("directory already exists: /")
        parent = self.resolve(str(p.parent))
        if not parent.is_dir:
            raise NotADirectoryError(str(p.parent))
        if p.name in parent.children:
            raise FileExistsError(f"File or directory exists: {p}")
        parent.children[p.name] = Node(p.name, True)

    def rmdir(self, path: str):
        p = self._normalize(path)
        if p == PurePosixPath("/"):
            raise PermissionError("cannot remove root")
        node = self.resolve(str(p))
        if not node.is_dir:
            raise NotADirectoryError(str(p))
        if node.children:
            raise OSError(f"Directory not empty: {p}")
        parent = self.resolve(str(p.parent))
        del parent.children[p.name]
        if self.cwd == p or str(self.cwd).startswith(str(p) + "/"):
            self.cwd = p.parent if p.parent != PurePosixPath("") else PurePosixPath("/")

    def pwd(self) -> str:
        return str(self.cwd)
