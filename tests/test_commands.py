from pathlib import Path

from src.commands import CommandError, Shell
from src.vfs import VFS


def shell(tmp_path: Path):
    (tmp_path / "file.txt").write_text(
        "line 1\nline 2\nline 3\nline 4\n", encoding="utf-8"
    )
    (tmp_path / "dir").mkdir()
    return Shell(VFS(tmp_path))


def test_ls(tmp_path):
    sh = shell(tmp_path)
    assert sh.execute("ls") == "dir\nfile.txt"


def test_cd(tmp_path):
    sh = shell(tmp_path)
    assert sh.execute("cd dir") == ""
    assert sh.vfs.pwd() == "/dir"


def test_head_default_and_n(tmp_path):
    sh = shell(tmp_path)
    assert sh.execute("head file.txt") == "line 1\nline 2\nline 3\nline 4"
    assert sh.execute("head -n 2 file.txt") == "line 1\nline 2"


def test_cal(tmp_path):
    sh = shell(tmp_path)
    out = sh.execute("cal 1 2025")
    assert "January 2025" in out


def test_touch_and_rmdir(tmp_path):
    sh = shell(tmp_path)
    sh.execute("touch new.txt")
    assert sh.vfs.exists("new.txt")
    sh.execute("rmdir dir")
    assert not sh.vfs.exists("dir")


def test_unknown_command(tmp_path):
    sh = shell(tmp_path)
    try:
        sh.execute("unknown")
    except CommandError as exc:
        assert "command not found" in str(exc)
    else:
        raise AssertionError("expected CommandError")


def test_invalid_arguments(tmp_path):
    sh = shell(tmp_path)
    try:
        sh.execute("cd")
    except CommandError as exc:
        assert "usage:" in str(exc)
    else:
        raise AssertionError("expected CommandError")
