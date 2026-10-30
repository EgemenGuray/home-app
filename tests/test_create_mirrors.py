"""create-mirrors.sh against a fake gh and git: private repos, branches and tags only."""
import os
import subprocess

from conftest import BASH, ROOT

BRAND = 'GITHUB_OWNER="octo"\nIOS_REPO="app-ios"\nANDROID_REPO="app-android"\n'


def run(tmp_path, brand=BRAND, existing=()):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    log = tmp_path / "calls.log"
    exists = "|".join(f"octo/{r}" for r in existing) or "none"
    (bin_dir / "gh").write_text(
        f'#!/usr/bin/env bash\necho "gh $*" >> "{log}"\n'
        f'[[ "$1 $2" == "repo view" ]] && case "$3" in {exists}) exit 0 ;; *) exit 1 ;; esac\nexit 0\n')
    (bin_dir / "git").write_text(
        f'#!/usr/bin/env bash\necho "git $*" >> "{log}"\n[[ "$1" == clone ]] && mkdir -p "${{@: -1}}"\nexit 0\n')
    for f in bin_dir.iterdir():
        f.chmod(0o755)
    (tmp_path / "brand.env").write_text(brand)
    env = {"PATH": f"{bin_dir}:/usr/bin:/bin", "BRAND_ENV": str(tmp_path / "brand.env"), "HOME": str(tmp_path)}
    r = subprocess.run([BASH, str(ROOT / "scripts/create-mirrors.sh")], env=env, capture_output=True, text=True)
    calls = log.read_text().splitlines() if log.exists() else []
    return r, calls


def test_creates_two_private_mirrors(tmp_path):
    r, calls = run(tmp_path)
    assert r.returncode == 0, r.stderr
    creates = [c for c in calls if c.startswith("gh repo create")]
    assert len(creates) == 2
    assert all("--private" in c and "--public" not in c for c in creates)
    assert "octo/app-ios" in creates[0] and "octo/app-android" in creates[1]


def test_pushes_only_branches_and_tags_from_upstream(tmp_path):
    _, calls = run(tmp_path)
    clones = [c for c in calls if c.startswith("git clone")]
    assert "https://github.com/home-assistant/iOS.git" in clones[0]
    assert "https://github.com/home-assistant/android.git" in clones[1]
    pushes = [c for c in calls if " push " in c]
    assert len(pushes) == 2
    for p in pushes:
        assert p.endswith("refs/heads/*:refs/heads/* refs/tags/*:refs/tags/*")
        assert "github.com/octo/" in p and "home-assistant" not in p.split(" push ")[1]


def test_skips_mirrors_that_exist(tmp_path):
    r, calls = run(tmp_path, existing=["app-ios"])
    assert "octo/app-ios exists; skipping." in r.stdout
    creates = [c for c in calls if c.startswith("gh repo create")]
    assert len(creates) == 1 and "octo/app-android" in creates[0]


def test_refuses_the_example_owner(tmp_path):
    r, calls = run(tmp_path, brand='GITHUB_OWNER="your-github-login"\nIOS_REPO="a"\nANDROID_REPO="b"\n')
    assert r.returncode == 1
    assert not [c for c in calls if "create" in c]


def test_needs_the_brand_file(tmp_path):
    env = {"PATH": "/usr/bin:/bin", "BRAND_ENV": str(tmp_path / "missing.env")}
    r = subprocess.run([BASH, str(ROOT / "scripts/create-mirrors.sh")], env=env, capture_output=True, text=True)
    assert r.returncode == 1 and "brand.env.example" in r.stderr


def test_example_brand_file_is_ignored_by_git():
    ignore = (ROOT / ".gitignore").read_text()
    assert "*.env" in ignore and "!*.env.example" in ignore
