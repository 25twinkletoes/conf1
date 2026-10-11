from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .commands import CommandError, Shell
from .vfs import VFS


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="UNIX-like shell emulator, variant 19")
    parser.add_argument("--vfs", required=True, help="path to physical VFS directory")
    parser.add_argument("--script", help="startup script with emulator commands")
    return parser.parse_args(argv)


def run_script(shell: Shell, script: str) -> int:
    path = Path(script)
    if not path.exists():
        print(f"script error: file not found: {path}", file=sys.stderr)
        return 1

    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        print(f"{shell.prompt()}{line}")
        try:
            output = shell.execute(line)
        except SystemExit:
            return 0
        except (CommandError, OSError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            print(f"script stopped at line {line_no}", file=sys.stderr)
            return 1
        if output:
            print(output)
    return 0


def repl(shell: Shell) -> int:
    while True:
        try:
            line = input(shell.prompt())
            output = shell.execute(line)
            if output:
                print(output)
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
        except SystemExit:
            return 0
        except (CommandError, OSError, ValueError) as exc:
            print(f"error: {exc}")


def main(argv=None):
    args = parse_args(argv)

    print(f"[debug] VFS: {Path(args.vfs).expanduser().resolve()}")
    print(f"[debug] script: {Path(args.script).expanduser().resolve() if args.script else '<interactive>'}")

    try:
        vfs = VFS(args.vfs)
    except (OSError, ValueError) as exc:
        print(f"error: cannot load VFS: {exc}", file=sys.stderr)
        return 1

    shell = Shell(vfs)
    return run_script(shell, args.script) if args.script else repl(shell)


if __name__ == "__main__":
    raise SystemExit(main())
