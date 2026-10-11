from pathlib import Path

from src.vfs import VFS


def make_vfs(tmp_path: Path):
    (tmp_path / "a.txt").write_text("one\ntwo\nthree\n", encoding="utf-8")
    (tmp_path / "dir").mkdir()
    return VFS(tmp_path)


def test_load_and_list(tmp_path):
    vfs = make_vfs(tmp_path)
    assert vfs.list_dir() == ["a.txt", "dir"]


def test_cd_and_pwd(tmp_path):
    vfs = make_vfs(tmp_path)
    vfs.change_dir("dir")
    assert vfs.pwd() == "/dir"


def test_touch_is_in_memory(tmp_path):
    vfs = make_vfs(tmp_path)
    vfs.touch("new.txt")
    assert vfs.exists("new.txt")
    assert not (tmp_path / "new.txt").exists()


def test_rmdir_empty_directory(tmp_path):
    vfs = make_vfs(tmp_path)
    vfs.rmdir("dir")
    assert not vfs.exists("dir")


def test_rmdir_non_empty_fails(tmp_path):
    vfs = make_vfs(tmp_path)
    (tmp_path / "dir" / "x").write_text("x", encoding="utf-8")
    vfs2 = VFS(tmp_path)
    try:
        vfs2.rmdir("dir")
    except OSError:
        pass
    else:
        raise AssertionError("expected OSError")
