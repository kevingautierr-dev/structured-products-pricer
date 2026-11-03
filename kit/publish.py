"""Put the day's slides online (public raw GitHub URLs) for Metricool.

Usage: python3 kit/publish.py RENDER_DIR YYYY-MM-DD
Run from the root of a checkout of the `newsmacro` branch of
github.com/kevingautierr-dev/structured-products-pricer.
Copies RENDER_DIR/NN.png (+ caption.txt, comment.txt, content.json if present)
into posts/YYYY-MM-DD/, commits, pushes, then checks that every image URL
answers 200 image/png. Prints a JSON list of the image URLs, in order.
"""
import json, pathlib, shutil, subprocess, sys, time, urllib.request

REPO = "kevingautierr-dev/structured-products-pricer"
BRANCH = "newsmacro"
TRAILER = ("Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"
           "Claude-Session: scheduled run (briefing et carrousel newsmacro)")


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def main():
    src, day = pathlib.Path(sys.argv[1]), sys.argv[2]
    dest = pathlib.Path("posts") / day
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    pngs = sorted(p for p in src.glob("[0-9][0-9].png"))
    if not pngs:
        sys.exit("no slides found")
    for p in pngs:
        shutil.copy2(p, dest / p.name)
    for extra in ("caption.txt", "comment.txt", "content.json"):
        if (src / extra).exists():
            shutil.copy2(src / extra, dest / extra)
    git("add", str(dest))
    if git("status", "--porcelain"):
        git("commit", "-m", f"newsmacro: carrousel du {day}", "-m", TRAILER)
    for attempt in range(3):
        try:
            git("push", "origin", f"HEAD:{BRANCH}")
            break
        except subprocess.CalledProcessError as ex:
            if attempt == 2:
                sys.exit("git push failed: " + (ex.stderr or ex.stdout))
            git("pull", "--rebase", "origin", BRANCH)
    sha = git("rev-parse", "HEAD")
    # Pin URLs to the commit so the raw CDN never serves a stale copy.
    urls = [f"https://raw.githubusercontent.com/{REPO}/{sha}/posts/{day}/{p.name}" for p in pngs]
    bad = []
    for u in urls:
        for attempt in range(6):
            try:
                with urllib.request.urlopen(u, timeout=20) as r:
                    if r.status == 200 and r.headers.get_content_type() == "image/png":
                        break
            except Exception:
                pass
            time.sleep(5)
        else:
            bad.append(u)
    print(json.dumps({"commit": sha, "urls": urls, "unreachable": bad}, indent=1))
    sys.exit(2 if bad else 0)


if __name__ == "__main__":
    main()
