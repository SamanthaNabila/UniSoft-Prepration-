# UniSoft Preparation

> ### 🚀 Live Demo — UniDesk Application
> **👉 [https://unidesk-demo.onrender.com/dashboard](https://unidesk-demo.onrender.com/dashboard)**
>
> *(Free hosting — the first visit may take ~1 minute to wake up.)*<br>
> So, this is a demo project. I'm sharing the details of two whitelisted accounts—one Employee and one Support Agent—so you can sign up and explore my application.
<br>
>  <b>Support Agent:</b> name:Jannatul <br> Email:jannatul@unidesk.com  <br>
> <b>Employee:</b> name:samantha <br>  Email:samantha@unidesk.com <br>



---

## What is this repository?

This is a **learning and preparation journal**. It documents a day-by-day journey
of practising **AI-assisted software engineering** — from understanding how AI
coding agents work, to comparing AI models, to designing specs and building real,
tested applications.

The work builds up to one capstone project: **UniDesk**, a complete full-stack
IT support ticketing system that is deployed and running live (link above).

**For non-technical readers:** think of this as a portfolio + notebook. Each
folder is one day of practice, with written notes explaining what was tried, what
was learned, and what worked or failed.

**For technical readers:** you'll find small Python CLIs, TDD katas, spec-first
builds, model benchmarking write-ups, an open-source contribution, and a
production-style FastAPI + React + PostgreSQL app.

---

## Repository Contents

### 📌 Capstone project

| Folder | What it is |
| --- | --- |
| **`UniDesk/`** | Full-stack IT support ticketing system — **FastAPI + PostgreSQL + React**, with JWT auth, role-based permissions (Employee vs Support Agent), a live dashboard, ticket lifecycle rules, comment threads, Docker deployment, and a pytest suite. See `UniDesk/README.md` for full details and local setup. **Live at the link at the top of this page.** |

### 📅 Daily practice

| Folder | Topic |
| --- | --- |
| `Day-01-Notes.md` | Product analysis — studying a real product (UniVAT): the problem it solves, its users, its data, and the impact if it went down. |
| `Day-02/` | Understanding the AI agent loop (*Understand → Plan → Act → Observe → Adjust*), plus a first hands-on lab exploring the Flask codebase. |
| `Day-03/` | **Notes CLI** — a Python command-line notes app built spec-first, milestone by milestone, with pytest. |
| `Day-04/` | Test-Driven Development kata — an invoice discount function with decimal rounding and full test coverage. |
| `Day-06/` | Notes CLI continued — bug hunting, edge cases, and expanded tests. |
| `Day-07/` | AI model comparison — vendor claims vs. actual benchmarks (DeepSeek-V4, GLM-5.2, Kimi K3). |
| `Day-08/` | Model head-to-head (Sonnet 5 vs. Haiku) measured on tokens, cost, speed, and code quality. |
| `Day-10/` | Open-source contribution — strengthening the thumbnail-recipe docs and tests for the `pyffmpegcore` project. |
| `Day-13/` | Lab report — how giving an AI a repo-context file (`CLAUDE.md`) improves code quality and prevents scope creep, tested on an Express + PostgreSQL task manager. |
| `Day-14/` | Feature spec + build — a Light/Dark mode toggle landing page (HTML, CSS, vanilla JS, localStorage). |
| `Day-15/` | Screenshot evidence from a practice session. |
| `Day-19-22/` | Reserved for upcoming work. |

### 📄 Root documents

| File | What it is |
| --- | --- |
| `UniSoft Preparation Hand-Note.pdf` | Consolidated handwritten notes covering the whole preparation. |
| `UniDesk/UniDesk HandNote.pdf` | Handwritten notes specific to the UniDesk build. |
| `Nabila Jannatul Ferdous Research Topic-1.pdf` | Research paper / topic write-up. |
| `render.yaml` | Deployment blueprint that runs the live UniDesk demo on Render. |

---

## Quick Start

- **Just want to see the result?** Open the live demo:
  **[https://unidesk-demo.onrender.com/dashboard](https://unidesk-demo.onrender.com/dashboard)**
- **Want to run UniDesk locally?** Follow `UniDesk/README.md` — it assumes no prior setup.
- **Want to read the journey?** Start at `Day-01-Notes.md` and go in order.
