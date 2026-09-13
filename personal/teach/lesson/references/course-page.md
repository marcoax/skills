# Warming up the course page

`index.html` is the single served page (ADR-0013/0015). Starting it lets the learner follow the
lesson in the browser while `/teach` works.

**Fail-soft at every step.** Anything missing or failing → skip silently and go to the hand-off.
The page is a companion, never a prerequisite.

1. **Already serving?** `curl -s -o /dev/null -w '%{http_code}' -m 1 http://localhost:8000/`.
   A `200` means a server is up — go to 3.

2. **Start one** from the repo root, in the background, with whatever this machine has — check
   with `command -v` first, don't assume:
   - `php -S localhost:8000 scripts/progress-server.php` — first choice: a Laravel learner has
     PHP, and the router enables the page's manual status marking (ADR-0018)
   - else `python3 -m http.server 8000` (or `python` where there is no `python3`)
   - neither available, or the port is held by something that isn't this repo → skip the page,
     say so in one line, move on

3. **Does `lessons/<slug>.html` exist?** Same basename as the URL fragment.
   - **Yes** → open `http://localhost:8000/#<slug>` with the platform opener (`open` on macOS,
     `xdg-open` on Linux, `start` on Windows). No opener → print the URL. This is the common case
     for a re-run, whose `.html` was written in an earlier session.
   - **No** → **don't open the browser.** It would poll an empty hash and look broken. Print the
     URL as plain text so the learner can open it by hand, say it will open by itself once the
     lesson HTML exists, and remember the pending state: open exactly once, the first time
     `/teach` writes that file.
