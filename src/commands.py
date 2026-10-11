from __future__ import annotations

import calendar
import datetime as dt
import getpass
import socket
from dataclasses import dataclass

from .vfs import VFS


class CommandError(Exception):
    pass


@dataclass
class Shell:
    vfs: VFS

    def prompt(self) -> str:
        return f"{getpass.getuser()}@{socket.gethostname()}:{self.vfs.pwd()}$ "

    def execute(self, line: str) -> str:
        line = line.strip()
        if not line:
            return ""
        parts = line.split()
        cmd, args = parts[0], parts[1:]

        handlers = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "head": self.cmd_head,
            "cal": self.cmd_cal,
            "touch": self.cmd_touch,
            "rmdir": self.cmd_rmdir,
            "exit": self.cmd_exit,
        }
        if cmd not in handlers:
            raise CommandError(f"{cmd}: command not found")
        return handlers[cmd](args)

    def _require(self, args, count, usage):
        if len(args) != count:
            raise CommandError(f"usage: {usage}")

    def cmd_ls(self, args):
        if len(args) > 1:
            raise CommandError("usage: ls [path]")
        return "\n".join(self.vfs.list_dir(args[0] if args else None))

    def cmd_cd(self, args):
        self._require(args, 1, "cd <path>")
        self.vfs.change_dir(args[0])
        return ""

    def cmd_head(self, args):
        if not args:
            raise CommandError("usage: head [-n N] <file>")
        n = 10
        if args[0] == "-n":
            if len(args) != 3:
                raise CommandError("usage: head [-n N] <file>")
            try:
                n = int(args[1])
            except ValueError:
                raise CommandError("head: invalid number of lines")
            if n < 0:
                raise CommandError("head: number of lines must be non-negative")
            path = args[2]
        elif len(args) == 1:
            path = args[0]
        else:
            raise CommandError("usage: head [-n N] <file>")
        lines = self.vfs.read_file(path).splitlines()
        return "\n".join(lines[:n])

    def cmd_cal(self, args):
        if len(args) > 2:
            raise CommandError("usage: cal [month year]")
        today = dt.date.today()
        if not args:
            month, year = today.month, today.year
        elif len(args) == 2:
            try:
                month, year = int(args[0]), int(args[1])
            except ValueError:
                raise CommandError("cal: month and year must be integers")
            if not 1 <= month <= 12:
                raise CommandError("cal: month must be 1..12")
        else:
            raise CommandError("usage: cal [month year]")
        return calendar.month(year, month).rstrip()

    def cmd_touch(self, args):
        self._require(args, 1, "touch <file>")
        self.vfs.touch(args[0])
        return ""

    def cmd_rmdir(self, args):
        self._require(args, 1, "rmdir <directory>")
        self.vfs.rmdir(args[0])
        return ""

    def cmd_exit(self, args):
        if args:
            raise CommandError("usage: exit")
        raise SystemExit(0)
