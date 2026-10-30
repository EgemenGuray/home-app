"""sync-upstream.sh with real git repos in a temp dir: merges upstream onto a review branch."""
import subprocess
from datetime import date

from conftest import BASH, ROOT, git

SCRIPT = str(ROOT / "scripts/sync-upstream.sh")


def commit(repo, name, text, msg):
    (repo / name).write_text(text)
    git(repo, "add", name)
    git(repo, "commit", "-qm", msg)


def setup(tmp):
    """upstream (the Companion repo), origin (the private mirror) and a local clone of origin."""
    upstream = tmp / "upstream"
    upstream.mkdir()
    git(upstream, "init", "-q")
    commit(upstream, "app.txt", "v1\n", "v1")
    git(tmp, "clone", "-q", "--bare", str(upstream), "origin.git")
    git(tmp, "clone", "-q", str(tmp / "origin.git"), "mirror")
    mirror = tmp / "mirror"
    git(mirror, "remote", "add", "upstream", str(upstream))
    git(mirror, "remote", "set-url", "--push", "upstream", "DISABLED")
    return upstream, mirror


def sync(mirror):
    return subprocess.run([BASH, SCRIPT, str(mirror)], capture_output=True, text=True)


def test_merges_upstream_onto_a_dated_branch_and_pushes_it(git_env):
    upstream, mirror = setup(git_env)
    commit(mirror, "brand.txt", "Home\n", "our branding")
    git(mirror, "push", "-q", "origin", "main")
    commit(upstream, "app.txt", "v2\n", "v2")

    r = sync(mirror)
    assert r.returncode == 0, r.stdout + r.stderr
    branch = f"sync/upstream-{date.today():%Y%m%d}"
    log = git(git_env, "--git-dir", str(git_env / "origin.git"), "log", "--format=%s", branch)
    assert log.splitlines()[0].startswith("Merge remote-tracking branch 'upstream/main'")
    assert {"v2", "our branding"} <= set(log.splitlines())
    # main itself is untouched: the merge waits for review.
    assert git(git_env, "--git-dir", str(git_env / "origin.git"), "log", "-1", "--format=%s", "main") == "our branding"


def test_stops_on_conflicts_without_pushing(git_env):
    upstream, mirror = setup(git_env)
    commit(mirror, "app.txt", "ours\n", "our change")
    git(mirror, "push", "-q", "origin", "main")
    commit(upstream, "app.txt", "theirs\n", "their change")

    r = sync(mirror)
    assert r.returncode == 1
    assert "Conflicts" in r.stdout
    assert "sync/" not in git(git_env, "--git-dir", str(git_env / "origin.git"), "branch")


def test_needs_the_upstream_remote(git_env):
    _, mirror = setup(git_env)
    git(mirror, "remote", "remove", "upstream")
    r = sync(mirror)
    assert r.returncode == 1
    assert "upstream remote" in r.stderr


def test_never_pushes_to_upstream(git_env):
    upstream, mirror = setup(git_env)
    commit(upstream, "app.txt", "v2\n", "v2")
    before = git(upstream, "rev-parse", "HEAD")
    assert sync(mirror).returncode == 0
    assert git(upstream, "rev-parse", "HEAD") == before
    assert git(upstream, "branch", "--list", "sync/*") == ""
