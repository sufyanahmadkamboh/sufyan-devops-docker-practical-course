# ruff: noqa: E501  (long lines are embedded CSS/HTML for the printed layout)
"""Build the study guide: study/study-guide.pdf.

Contents: how to study, the method and the diagrams, a summary of every lesson (what it teaches, its diagram, its
command table, its recap) module by module, the troubleshooting problems, the projects, the capstone, the command
reference, the glossary and the interview questions. The full lessons (with every command and output) stay in the
repository; the PDF is the companion for revision.

Usage:
    pip install markdown
    python study/tools/build_pdf.py            # prints the PDF with a headless Chrome or Edge (set BROWSER if needed)
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

STUDY = Path(__file__).resolve().parents[1]
REPO = STUDY.parent
OUT = STUDY / "study-guide.pdf"
REPO_URL = "https://github.com/sufyanahmadkamboh/sufyan-devops-docker-practical-course"
MODULES = sorted(p for p in REPO.glob("[0-2][0-9]-*") if p.is_dir() and list(p.glob("[0-9][0-9][0-9]-*/README.md")))
TAIL = ["17-troubleshooting/README.md", "21-projects/README.md", "22-capstone/README.md", "docs/command-reference.md",
        "docs/glossary.md", "docs/interview-questions.md"]
MD_EXT = ["tables", "fenced_code", "md_in_html", "sane_lists"]

CSS = """
@page { size: A4; margin: 15mm 14mm 15mm 14mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", "Inter", Arial, sans-serif; font-size: 10.3pt; line-height: 1.5; color: #1a1f2b; margin: 0; }
h1 { font-size: 21pt; color: #0b4f8a; border-bottom: 3px solid #1d8fe1; padding-bottom: 6px; margin: 0 0 14px; }
h2 { font-size: 13.5pt; color: #0f62b0; margin: 18px 0 6px; }
h3 { font-size: 11.5pt; margin: 12px 0 5px; }
p { margin: 5px 0; }
a { color: #0f62b0; text-decoration: none; }
code { font-family: Consolas, "Cascadia Mono", monospace; font-size: 8.8pt; background: #e8f2fc; padding: 1px 4px; border-radius: 3px; }
pre { background: #111827; color: #e6edf6; padding: 9px 11px; border-radius: 6px; overflow: hidden; white-space: pre-wrap;
      word-break: break-word; font-size: 8.2pt; line-height: 1.4; break-inside: avoid; }
pre code { background: none; color: inherit; padding: 0; font-size: inherit; }
table { border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 8.9pt; break-inside: auto; }
th, td { border: 1px solid #c9dbee; padding: 4px 6px; vertical-align: top; text-align: left; }
th { background: #e8f2fc; color: #0b4f8a; }
tr { break-inside: avoid; }
blockquote { border-left: 4px solid #1d8fe1; background: #f3f8fe; margin: 8px 0; padding: 5px 11px; }
img { max-width: 100%; border: 1px solid #c9dbee; border-radius: 6px; margin: 4px 0 8px; }
details { background: #f3f8fe; border: 1px solid #c9dbee; border-radius: 6px; padding: 5px 11px; margin: 6px 0; }
details summary { font-weight: 600; color: #0f62b0; }
.chapter { break-before: page; }
.lesson { break-inside: avoid-page; border-top: 1px solid #d6e6f6; padding-top: 4px; }
.lesson h2 { margin-top: 10px; }
.label { font-size: 8.5pt; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: #0b4f8a; margin-top: 6px; }
.cover { height: 262mm; display: flex; flex-direction: column; justify-content: center; padding: 0 10mm;
         background: linear-gradient(160deg, #06192e 0%, #0b2e52 55%, #0f62b0 100%); color: #e8f2fc; border-radius: 10px; }
.cover .kicker { color: #8ec9ff; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; font-size: 10pt; }
.cover h1 { color: #fff; border: 0; font-size: 30pt; line-height: 1.15; margin: 10px 0 14px; }
.cover p { color: #d6ebff; font-size: 12.3pt; }
.cover .who { margin-top: 40px; font-size: 11pt; color: #8ec9ff; }
.toc { break-before: page; }
.toc ul { font-size: 11pt; line-height: 1.95; list-style: none; padding-left: 0; }
"""


def find_browser() -> str:
    for c in [os.environ.get("BROWSER", ""), r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe", shutil.which("google-chrome") or "",
              shutil.which("chromium") or "", shutil.which("chromium-browser") or "", shutil.which("microsoft-edge") or ""]:
        if c and Path(c).exists():
            return c
    sys.exit("No Chromium-based browser found. Set BROWSER=/path/to/chrome")


def anchor(rel: str) -> str:
    return re.sub(r"[^a-z0-9-]", "-", rel.lower()).removesuffix("-md")


def clean(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)                      # test annotations
    return re.sub(r"^Next: .*$", "", text, flags=re.M)                      # GitHub-only navigation


def render(text: str, path: Path) -> str:
    def details(m: re.Match) -> str:                                         # answers open in print
        summary = markdown.markdown(m.group(1)).removeprefix("<p>").removesuffix("</p>")
        inner = markdown.markdown(m.group(2).strip(), extensions=["fenced_code", "tables", "sane_lists"])
        return f"\n<details open><summary>{summary}</summary>{inner}</details>\n"

    text = re.sub(r"<details>\s*<summary>(.*?)</summary>(.*?)</details>", details, text, flags=re.S)
    html = markdown.markdown(text, extensions=MD_EXT)

    def link(m: re.Match) -> str:                                            # relative links → GitHub
        attr, href = m.group(1), m.group(2)
        if href.startswith(("http", "#", "mailto:", "file:")):
            return m.group(0)
        base, _, frag = href.partition("#")
        target = (path.parent / base).resolve()
        if attr == "src":                                                    # images: embed from disk
            return f'src="{target.as_uri()}"'
        rel = target.relative_to(REPO).as_posix() if target.is_relative_to(REPO) else base
        kind = "tree" if target.is_dir() else "blob"
        return f'href="{REPO_URL}/{kind}/main/{rel}' + (f"#{frag}" if frag else "") + '"'

    return re.sub(r'(href|src)="([^"]+)"', link, html)


def section(text: str, name: str, level: int = 2) -> str:
    """The body of the heading `name` (at `level`), up to the next heading of the same or a higher level.
    Lines inside fenced code blocks are never headings (outputs can contain "# Cafe")."""
    out, inside, fence = [], False, False
    for ln in text.split("\n"):
        if ln.startswith("```"):
            fence = not fence
        heading = None if fence or ln.startswith("```") else re_heading(ln)
        if heading and heading[0] <= level:
            if inside:
                break
            inside = heading[0] == level and heading[1] == name
            continue
        if inside:
            out.append(ln)
    return "\n".join(out).strip()


def re_heading(ln: str):
    m = re.match(r"^(#{1,6}) (.+?)\s*$", ln)
    return (len(m.group(1)), m.group(2)) if m else None



def lesson_summary(readme: Path) -> str:
    text = clean(readme.read_text(encoding="utf-8"))
    title = re.search(r"^# (.+)$", text, re.M).group(1)
    parts = [f"## {title}"]
    for name, label in [("What are we learning?", ""), ("Visual", "Visual"), ("Command breakdown", "Commands"),
                        ("Recap", "Recap")]:
        body = section(text, name)
        if body:
            parts.append((f'<div class="label">{label}</div>\n\n' if label else "") + body)
    link = f"{REPO_URL}/blob/main/{readme.relative_to(REPO).as_posix()}"
    parts.append(f"Full lesson with every command and its real output: [{readme.parent.name}]({link})")
    return '<div class="lesson" markdown="1">\n\n' + "\n\n".join(parts) + "\n\n</div>"


def module_chapter(mod: Path) -> tuple[str, str, str]:
    intro = clean((mod / "README.md").read_text(encoding="utf-8"))
    title = re.search(r"^# (.+)$", intro, re.M).group(1)
    body = f"# {title}\n\n" + "\n\n".join(lesson_summary(p) for p in sorted(mod.glob("[0-9][0-9][0-9]-*/README.md")))
    return anchor(mod.name), title, render(body, mod / "README.md")


def file_chapter(rel: str) -> tuple[str, str, str]:
    path = REPO / rel
    text = clean(path.read_text(encoding="utf-8"))
    return anchor(rel), re.search(r"^#\s+(.+)$", text, re.M).group(1), render(text, path)


def overview_chapter() -> tuple[str, str, str]:
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    method = section(readme, "How a lesson works")
    diagrams = "\n\n".join(f"![{p.stem}]({p.relative_to(REPO).as_posix()})" for p in sorted((REPO / "diagrams").glob("*.svg")))
    text = f"# The method and the big picture\n\n## How a lesson works\n\n{method}\n\n## Diagrams\n\n{diagrams}"
    return "overview", "The method and the big picture", render(text, REPO / "README.md")


def main() -> None:
    chapters = [file_chapter("study/README.md"), overview_chapter()]
    chapters += [module_chapter(m) for m in MODULES]
    chapters += [file_chapter(r) for r in TAIL]
    toc = "".join(f'<li><a href="#{a}">{t}</a></li>' for a, t, _ in chapters)
    parts = "".join(f'<section class="chapter" id="{a}">{h}</section>' for a, _, h in chapters)
    questions = len(re.findall(r"^\*\*\d+\. ", (REPO / "docs/interview-questions.md").read_text(encoding="utf-8"), re.M))
    lessons = sum(len(list(m.glob("[0-9][0-9][0-9]-*/README.md"))) for m in MODULES)
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Study guide: Docker Practical Course</title><style>{CSS}</style></head><body>
<div class="cover">
  <div class="kicker">Study guide · Docker · from beginner to advanced</div>
  <h1>Docker Practical Course<br>Docker From Beginner to Advanced</h1>
  <p>Every one of the {lessons} lessons on a page or less: what it teaches, its diagram, its commands and its recap. Then
     the 25 troubleshooting problems by symptom, the projects, the capstone, the command reference, a glossary and
     {questions} interview questions.</p>
  <p class="who">Sufyan Ahmad · DevOps Engineer<br>{REPO_URL}</p>
</div>
<div class="toc"><h1>Contents</h1><ul>{toc}</ul>
<p>The full lessons, with every command and its real, tested output, the exercises, challenges, assessments,
troubleshooting labs and projects, are in the repository.</p></div>
{parts}
</body></html>"""
    browser = find_browser()
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "study-guide.html"
        page.write_text(doc, encoding="utf-8")
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--disable-extensions", "--disable-sync",
                        "--no-first-run", "--no-pdf-header-footer", "--allow-file-access-from-files",
                        f"--user-data-dir={Path(tmp) / 'profile'}", f"--print-to-pdf={OUT}", page.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"wrote {OUT.relative_to(REPO)} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
