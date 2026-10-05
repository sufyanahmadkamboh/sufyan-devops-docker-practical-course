"""Generate each lesson's companion files from its README.md.

Every lesson is written once, in README.md, with these sections (among others):

    ## Hands-on lab                                   -> lab.md
    ## Practice challenge (without the solution)      -> challenge.md
    ## Practice challenge (the <details> solution)    -> solution.md
    ## Break it, ## Troubleshoot it, ## Fix it        -> troubleshooting.md
    every ```bash block, under its section title      -> commands.md

    python tools/lesson_files.py            write the files
    python tools/lesson_files.py --check    fail if any file is missing or out of date (CI)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS = sorted(ROOT.glob("[0-2][0-9]-*/[0-9][0-9][0-9]-*/README.md"))
HEADER = "<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->\n"


def sections(text: str) -> list[tuple[str, str]]:
    """(title, body) for every '## ' section, in order. Lines inside fenced code blocks are never headings."""
    out, title, body, fence = [], None, [], False
    for line in text.split("\n"):
        if line.startswith("```"):
            fence = not fence
        if not fence and line.startswith("## "):
            if title is not None:
                out.append((title, "\n".join(body)))
            title, body = line[3:].strip(), []
        elif title is not None:
            body.append(line)
    if title is not None:
        out.append((title, "\n".join(body)))
    return out


def strip_tests(body: str) -> str:
    """Test annotations are for the runner; the companion files are for reading."""
    body = re.sub(r"^<!-- test(-run)?[^>]*-->\n\n?", "", body, flags=re.M)
    return re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"


def relink(body: str) -> str:
    return re.sub(r"\]\(#([^)]+)\)", r"](README.md#\1)", body)


DETAILS = re.compile(r"<details>\s*<summary>.*?</summary>(.*?)</details>", re.S)


def build(readme: Path) -> dict[str, str]:
    text = readme.read_text(encoding="utf-8")
    title = re.search(r"^# (.+)$", text, re.M).group(1)
    secs = dict(sections(text))
    out = {}

    def page(kind: str, names: list[str], transform=lambda b: b) -> str:
        found = [(n, secs[n]) for n in names if n in secs]
        if not found:
            raise SystemExit(f"{readme.relative_to(ROOT)}: missing section(s) {names}")
        body = "".join(f"## {n}\n\n{relink(strip_tests(transform(b)))}\n" for n, b in found)
        return f"{HEADER}# {title} · {kind}\n\n> The full lesson: [README.md](README.md)\n\n{body}".rstrip() + "\n"

    out["lab.md"] = page("hands-on lab", ["Hands-on lab"])
    out["troubleshooting.md"] = page("troubleshooting", ["Break it", "Troubleshoot it", "Fix it"])
    out["challenge.md"] = page("challenge", ["Practice challenge"],
                               lambda b: DETAILS.sub("The solution is in [solution.md](solution.md).", b))
    challenge = secs.get("Practice challenge", "")
    solution = DETAILS.search(challenge)
    if not solution:
        raise SystemExit(f"{readme.relative_to(ROOT)}: the practice challenge has no <details> solution")
    task = DETAILS.sub("", challenge)
    out["solution.md"] = (f"{HEADER}# {title} · solution\n\n> Try the [challenge](challenge.md) first. The full lesson: "
                          f"[README.md](README.md)\n\n## The challenge\n\n{relink(strip_tests(task))}\n"
                          f"## Solution\n\n{relink(strip_tests(solution.group(1)))}").rstrip() + "\n"

    cmds = []
    for sec, body in sections(text):
        blocks = re.findall(r"^```bash\n(.*?)^```", body, flags=re.M | re.S)
        if blocks:
            cmds.append(f"## {sec}\n\n" + "\n".join(f"```bash\n{b}```\n" for b in blocks))
    out["commands.md"] = (f"{HEADER}# {title} · commands\n\n> Every command of the lesson, in order. The explanations: "
                          f"[README.md](README.md)\n\n" + "\n".join(cmds))
    return out


def main() -> int:
    check = "--check" in sys.argv
    stale = []
    for readme in LESSONS:
        for name, content in build(readme).items():
            target = readme.parent / name
            if check:
                if not target.exists() or target.read_text(encoding="utf-8") != content:
                    stale.append(str(target.relative_to(ROOT)))
            else:
                target.write_text(content, encoding="utf-8", newline="\n")
    if check and stale:
        print("out of date (run python tools/lesson_files.py):\n  " + "\n  ".join(stale))
        return 1
    print(f"{len(LESSONS)} lessons {'checked' if check else 'written'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
