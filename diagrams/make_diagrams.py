"""Generate the course diagrams (SVG) in one consistent style.

    python diagrams/make_diagrams.py        writes diagrams/*.svg

Each diagram is described with a few primitives (boxes, arrows, labels), so they stay editable and match.
"""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent
FONT = "Segoe UI, Helvetica, Arial, sans-serif"
MONO = "Cascadia Code, Consolas, Menlo, monospace"
INK, MUTED, LINE, BG = "#1f2937", "#5b6472", "#c9d1dc", "#ffffff"
BLUE, GREEN, ORANGE, PURPLE, RED, TEAL = "#1d63ed", "#16a34a", "#ea7a0c", "#7c3aed", "#dc2626", "#0d9488"


class Svg:
    def __init__(self, w: int, h: int, title: str):
        self.w, self.h, self.parts = w, h, []
        self.parts.append(f'<rect width="{w}" height="{h}" rx="14" fill="{BG}"/>')
        self.text(24, 38, title, size=20, weight=700)

    def text(self, x, y, s, size=14, color=INK, weight=400, anchor="start", mono=False):
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        fam = MONO if mono else FONT
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" '
                          f'fill="{color}" text-anchor="{anchor}" xml:space="preserve">{s}</text>')

    def box(self, x, y, w, h, title, sub="", color=BLUE, fill=None, dashed=False):
        fill = fill or color + "14"
        dash = ' stroke-dasharray="7 5"' if dashed else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{color}" '
                          f'stroke-width="2"{dash}/>')
        if title:
            self.text(x + w / 2, y + (h / 2 + 5 if not sub else h / 2 - 6), title, size=15, weight=700,
                      anchor="middle", color=color)
        if sub:
            self.text(x + w / 2, y + h / 2 + 15, sub, size=12, color=MUTED, anchor="middle")

    def frame(self, x, y, w, h, label, color=MUTED):
        """A dashed area (a host, a network, a stage) with its label at the top left."""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="none" stroke="{color}" '
                          f'stroke-width="1.8" stroke-dasharray="7 5"/>')
        self.text(x + 12, y + 20, label, size=12, weight=700, color=color)

    def arrow(self, x1, y1, x2, y2, label="", color=MUTED, above=True, dashed=False):
        mid = f"a{len(self.parts)}"
        dash = ' stroke-dasharray="6 5"' if dashed else ""
        self.parts.append(f'<defs><marker id="{mid}" markerWidth="11" markerHeight="11" refX="9" refY="5" orient="auto" '
                          f'markerUnits="userSpaceOnUse"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker></defs>')
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2.2"{dash} '
                          f'marker-end="url(#{mid})"/>')
        if label:
            self.text((x1 + x2) / 2, (y1 + y2) / 2 + (-9 if above else 20), label, size=13, anchor="middle",
                      color=color, mono=True)

    def save(self, name: str):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
               f'height="{self.h}" role="img" aria-label="{name}">' + "".join(self.parts) + "</svg>\n")
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8", newline="\n")
        print(f"wrote diagrams/{name}.svg")


def architecture():
    d = Svg(1000, 380, "Docker architecture: the client asks, the engine works")
    d.box(30, 150, 170, 80, "docker CLI", "the client", ORANGE)
    d.frame(250, 70, 540, 290, "Docker host (Docker Desktop: a small Linux VM)")
    d.box(280, 110, 200, 70, "dockerd", "images · networks · volumes", BLUE)
    d.box(280, 200, 200, 55, "containerd", "", PURPLE)
    d.box(280, 275, 200, 55, "runc", "", PURPLE)
    for i, name in enumerate(["web", "api", "db"]):
        d.box(540 + i * 76, 260, 64, 70, name, "", GREEN)
    d.arrow(200, 190, 278, 150, "REST API", above=False)
    d.arrow(380, 180, 380, 198)
    d.arrow(380, 255, 380, 273)
    d.arrow(480, 300, 536, 300)
    d.box(830, 140, 150, 90, "Registry", "Docker Hub · GHCR", TEAL)
    d.arrow(482, 140, 826, 170, "pull / push")
    d.text(540, 248, "containers: isolated processes", size=12, color=MUTED)
    d.save("docker-architecture")


def containers_vs_vms():
    d = Svg(1000, 400, "Virtual machines vs containers")
    d.text(242, 72, "Virtual machines", size=15, weight=700, anchor="middle")
    d.text(742, 72, "Containers", size=15, weight=700, anchor="middle")
    for i in range(3):
        x = 40 + i * 140
        d.box(x, 90, 125, 40, f"App {'ABC'[i]}", "", GREEN)
        d.box(x, 135, 125, 40, "Libraries", "", TEAL)
        d.box(x, 180, 125, 55, "Guest OS", "+ its own kernel", RED)
    d.box(40, 245, 405, 45, "Hypervisor", "", PURPLE)
    d.box(40, 300, 405, 45, "Hardware", "", MUTED)
    for i in range(3):
        x = 540 + i * 140
        d.box(x, 90, 125, 40, f"App {'ABC'[i]}", "", GREEN)
        d.box(x, 135, 125, 40, "Libraries", "", TEAL)
    d.box(540, 190, 405, 45, "Container engine (Docker)", "", BLUE)
    d.box(540, 245, 405, 45, "Host OS + one shared kernel", "", ORANGE)
    d.box(540, 300, 405, 45, "Hardware", "", MUTED)
    d.text(242, 375, "minutes to boot · GBs per VM · strong isolation", size=13, color=MUTED, anchor="middle")
    d.text(742, 375, "< 1 s to start · MBs per image · process isolation", size=13, color=MUTED, anchor="middle")
    d.save("containers-vs-vms")


def image_layers():
    d = Svg(1000, 390, "Images are layers; a container adds one writable layer")
    layers = [("FROM node:24-alpine", MUTED), ("WORKDIR /app", TEAL), ("COPY package*.json ./", TEAL),
              ("RUN npm ci", PURPLE), ("COPY . .", BLUE)]
    for i, (t, c) in enumerate(reversed(layers)):
        d.box(60, 80 + i * 52, 380, 44, t, "", c)
    d.text(250, 362, "read-only · shared by every container of the image", size=13, color=MUTED, anchor="middle")
    for j, name in enumerate(["container 1", "container 2"]):
        x = 540 + j * 220
        d.box(x, 80, 190, 60, "writable layer", name, ORANGE, dashed=True)
        d.arrow(x + 95, 142, 442, 104 + j * 30, dashed=True)
    d.text(560, 200, "the writable layer is deleted with the container:", size=13, color=MUTED)
    d.text(560, 222, "keep data in volumes (lesson 055)", size=13, color=MUTED)
    d.save("image-layers")


def lifecycle():
    d = Svg(1000, 330, "Container lifecycle")
    for name, x, c in [("created", 60, PURPLE), ("running", 290, GREEN), ("exited", 520, ORANGE), ("removed", 780, MUTED)]:
        d.box(x, 130, 160, 70, name, "", c)
    d.arrow(222, 165, 288, 165, "start")
    d.arrow(452, 152, 518, 152, "stop · exit")
    d.arrow(518, 185, 452, 185, "start", above=False)
    d.arrow(682, 165, 778, 165, "rm")
    d.box(290, 245, 160, 55, "paused", "", TEAL)
    d.arrow(350, 202, 350, 243)
    d.arrow(390, 243, 390, 202)
    d.text(470, 277, "pause / unpause", size=13, color=MUTED, mono=True)
    d.text(60, 100, "docker create", size=13, color=MUTED, mono=True)
    d.text(290, 100, "docker run = create + start", size=13, color=MUTED, mono=True)
    d.text(600, 100, "exit codes: 0 1 127 137 143", size=13, color=MUTED, mono=True)
    d.save("container-lifecycle")


def build_flow():
    d = Svg(1000, 300, "From Dockerfile to running container")
    steps = [("Dockerfile", "+ build context", ORANGE), ("docker build", "cache per step", PURPLE),
             ("Image", "name:tag · digest", BLUE), ("Registry", "push / pull", TEAL), ("Container", "docker run", GREEN)]
    for i, (t, s, c) in enumerate(steps):
        d.box(20 + i * 196, 110, 160, 80, t, s, c)
        if i:
            d.arrow(20 + i * 196 - 34, 150, 20 + i * 196 - 2, 150)
    d.text(500, 245, ".dockerignore keeps secrets and junk out of the context · tags move, digests do not",
           size=13, color=MUTED, anchor="middle")
    d.save("build-flow")


def networking():
    d = Svg(1000, 400, "Networking: publish to the host, talk by name inside")
    d.frame(30, 60, 940, 320, "Docker host")
    d.box(60, 125, 150, 70, "host :8080", "-p 8080:80", ORANGE)
    d.frame(260, 90, 690, 270, 'user-defined network "cafe"', BLUE)
    d.box(290, 130, 170, 70, "web", "nginx :80", GREEN)
    d.box(540, 130, 170, 70, "api", ":8000", GREEN)
    d.box(780, 130, 150, 70, "db", ":5432", GREEN)
    d.arrow(212, 160, 288, 165)
    d.arrow(462, 165, 538, 165, "api:8000")
    d.arrow(712, 165, 778, 165)
    d.box(440, 270, 280, 60, "embedded DNS 127.0.0.11", "service name → container IP", PURPLE)
    d.text(290, 235, "only web is published; api and db are reachable only inside the network", size=12, color=MUTED)
    d.save("networking")


def storage():
    d = Svg(1000, 360, "Where container data lives")
    d.box(40, 80, 280, 90, "writable layer", "dies with the container", RED)
    d.box(360, 80, 280, 90, "named volume", "managed by Docker · survives", GREEN)
    d.box(680, 80, 280, 90, "bind mount", "a host folder · you manage it", BLUE)
    for x, cmd in [(180, "(nothing to add)"), (500, "-v pgdata:/var/lib/postgresql"), (820, '-v "$(pwd)":/app')]:
        d.text(x, 205, cmd, size=13, mono=True, anchor="middle", color=MUTED)
    for x, use in [(180, "temporary files only"), (500, "databases, uploads"), (820, "source code in development")]:
        d.text(x, 240, use, size=14, anchor="middle")
    d.box(360, 275, 280, 55, "tmpfs", "in memory · for --read-only", TEAL)
    d.save("storage")


def compose():
    d = Svg(1000, 380, "Docker Compose: the whole application in one file")
    d.box(30, 120, 200, 130, "compose.yaml", "services · networks · volumes", ORANGE)
    d.arrow(232, 185, 306, 185, "up --wait")
    d.frame(310, 70, 660, 290, "project", BLUE)
    for i, (name, sub) in enumerate([("proxy", "ports: 8080"), ("api", "depends_on: healthy"), ("db", "healthcheck")]):
        d.box(340 + i * 210, 120, 180, 70, name, sub, GREEN)
    d.arrow(522, 155, 548, 155)
    d.arrow(732, 155, 758, 155)
    d.box(760, 240, 180, 55, "volume pgdata", "", PURPLE)
    d.arrow(850, 192, 850, 238)
    d.box(340, 240, 390, 55, "networks: edge, backend", "service names are DNS names", TEAL)
    d.save("compose")


def multistage():
    d = Svg(1000, 330, "Multi-stage build: compile big, ship small")
    d.frame(30, 70, 430, 220, "stage build: golang:1.26-alpine", PURPLE)
    d.box(60, 110, 170, 60, "Go toolchain", "", MUTED)
    d.box(250, 110, 180, 60, "source + modules", "", MUTED)
    d.box(150, 200, 200, 60, "/out/api", "static binary", BLUE)
    d.frame(560, 70, 410, 220, "final: distroless static, nonroot", GREEN)
    d.box(660, 150, 200, 60, "/api", "only this is shipped", GREEN)
    d.arrow(352, 230, 658, 182, "COPY --from=build")
    d.text(500, 318, "lesson 091 measures the difference on real images", size=13, color=MUTED, anchor="middle")
    d.save("multistage")


def security():
    d = Svg(1000, 380, "Container hardening, layer by layer")
    items = [("minimal, pinned base", "fewer packages, fewer CVEs", TEAL), ("non-root USER", "not uid 0", GREEN),
             ("read-only root file system", "+ tmpfs where needed", BLUE), ("cap_drop: ALL", "add back only what is needed", PURPLE),
             ("no-new-privileges", "no setuid escalation", ORANGE), ("memory · CPU · pids limits", "one container cannot starve the host", RED)]
    for i, (t, s, c) in enumerate(items):
        d.box(40 + (i % 3) * 315, 80 + (i // 3) * 130, 290, 100, t, s, c)
    d.text(500, 355, "secrets as files at run time, never in ENV, ARG or a layer · never mount docker.sock",
           size=13, color=MUTED, anchor="middle")
    d.save("security")


def capstone():
    d = Svg(1000, 420, "Capstone: a production-style stack")
    d.box(30, 160, 140, 70, "browser", "localhost:8080", ORANGE)
    d.frame(200, 60, 520, 180, 'network "edge"', BLUE)
    d.box(230, 140, 150, 70, "proxy", "nginx · non-root", GREEN)
    d.box(530, 90, 160, 60, "frontend", "nginx · static", GREEN)
    d.box(530, 165, 160, 60, "api", "Go · distroless", GREEN)
    d.frame(480, 255, 490, 150, 'network "backend" (internal)', PURPLE)
    d.box(530, 300, 160, 70, "db", "PostgreSQL 18", PURPLE)
    d.box(770, 300, 170, 70, "volume pgdata", "", TEAL)
    d.arrow(172, 195, 228, 178)
    d.arrow(382, 165, 528, 122, "/")
    d.arrow(382, 185, 528, 195, "/api/", above=False)
    d.arrow(610, 227, 610, 298)
    d.arrow(692, 335, 768, 335)
    d.box(760, 90, 200, 120, "secret", "db_password", RED, dashed=True)
    d.save("capstone")


def troubleshooting():
    d = Svg(1000, 300, "The troubleshooting method")
    steps = [("Symptom", "what exactly fails?", RED), ("docker ps -a", "state · exit code", ORANGE),
             ("docker logs", "the app's words", PURPLE), ("docker inspect", "config · mounts", BLUE),
             ("docker exec", "test from inside", TEAL), ("Fix + verify", "then prevent", GREEN)]
    for i, (t, s, c) in enumerate(steps):
        d.box(15 + i * 164, 110, 146, 80, t, s, c)
        if i:
            d.arrow(15 + i * 164 - 16, 150, 15 + i * 164 - 2, 150)
    d.text(500, 245, "the 25 problems of module 17 follow these steps, from symptom to prevention",
           size=13, color=MUTED, anchor="middle")
    d.save("troubleshooting")


if __name__ == "__main__":
    for make in [architecture, containers_vs_vms, image_layers, lifecycle, build_flow, networking, storage, compose,
                 multistage, security, capstone, troubleshooting]:
        make()
