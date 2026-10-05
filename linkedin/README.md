# LinkedIn package

| File | Use |
|---|---|
| `post.md` | Post text |
| `carousel/carousel.pdf` | **Recommended:** upload as a *Document* post. LinkedIn shows it as a swipeable carousel |
| `carousel/slide-01.png` … `slide-11.png` | The same slides as images (1080×1350), for a multi-image post |
| `carousel/slides.html` | Source of the slides; re-render a slide with a headless browser (`slides.html?s=N`) |
| `carousel/qr-repo.svg`, `qr-portfolio.svg` | The QR codes used on the last slide |
| `project-image.png` | Single overview image (1200×627), from `project-image.html` |
| `project-summary.md` | Short technical summary |
| `hashtags.txt` | Hashtags |

## The slides (one picture per idea)

| # | Visual | Message |
|---|---|---|
| 1 | Four numbers: lessons, troubleshooting problems, tested blocks, projects | What it is |
| 2 | Seven real error messages from the course | The pain |
| 3 | The eleven-step loop with Break / Troubleshoot / Fix highlighted | The method |
| 4 | Dockerfile layers in cache order | Concept: layers and the build cache |
| 5 | The same Go API measured three ways | Concept: multi-stage builds |
| 6 | Published proxy, service names, an internal network | Concept: networking |
| 7 | Real `docker inspect` output and blocked writes | Concept: hardening, verified |
| 8 | The capstone stack, healthy, broken and recovered | The capstone |
| 9 | Tiles: assessments, exam, videos, PDF | What is inside |
| 10 | A test annotation on a lesson block | Every command tested |
| 11 | QR codes to the course and the portfolio, and a question | Links |

## How to post

1. Create a post, choose **Add a document**, upload `carousel/carousel.pdf` and give it the title
   "Docker, from beginner to advanced".
2. Paste `post.md` as the text (the hashtags are at the end).
3. Reply to comments within the first hour.
