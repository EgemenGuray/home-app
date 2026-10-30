import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
BASH = shutil.which("bash")
GIT = shutil.which("git")


def git(cwd, *args):
    return subprocess.run([GIT, *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def git_env(tmp_path, monkeypatch):
    """A throwaway git identity, so tests never touch the real one."""
    home = tmp_path / "home"
    home.mkdir()
    for k, v in {"HOME": str(home), "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "Test",
                 "GIT_AUTHOR_EMAIL": "test@example.com", "GIT_COMMITTER_NAME": "Test",
                 "GIT_COMMITTER_EMAIL": "test@example.com"}.items():
        monkeypatch.setenv(k, v)
    git(tmp_path, "config", "--global", "init.defaultBranch", "main")
    return tmp_path
