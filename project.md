# WFM Lifts — Starting Strength Progression Tracker

**"No fake gains. Only truth."**

A mobile-first, brutally honest Starting Strength progression app. You log what you actually lift — not what you wish you lifted. Progression is earned, not automatic.

## Summary

WFM Lifts is a Flask web app that enforces the true rules of Starting Strength:
- Full warmup ladders with perfect plate math
- Real-time working weight editing
- Actual weight per work set logged
- Only successful workouts earn +5 lb
- Failed or deloaded lifts → next session uses what you actually did
- Full history of every rep, every failure, every triumph

Built for lifters who respect the program.

## High-Level Architecture (Mermaid)

```mermaid
graph TD
    A[Browser / Mobile] -->|HTTPS| B[Flask App]
    B --> C[PostgreSQL DB]
    B --> D[Flask-Login]
    B --> E[Flask-SQLAlchemy]
    B --> F[Flask-Migrate]
    B --> G[Jinja2 Templates]
    B --> H[Static: CSS + JS]

    subgraph Models
        C --> I[User]
        C --> J[StartingWeights]
        C --> K[WorkoutLog]
        C --> L[LiftEntry]
    end

    subgraph Features
        B --> M[Dashboard: Today's Workout]
        B --> N[Actual Weight Inputs]
        B --> O[Complete Workout → Progression Logic]
        B --> P[History Page (next)]
    end
```

## Tech Stack & Versions (as of Dec 2025)

| Component           | Version / Choice            |
|---------------------|-----------------------------|
| Python              | 3.11+                       |
| Flask               | 3.0+                        |
| Flask-Login         | latest                      |
| Flask-SQLAlchemy    | latest                      |
| Flask-Migrate       | latest                      |
| Flask-WTF           | latest                      |
| PostgreSQL          | 16+ (local + Render)        |
| psycopg2-binary     | latest                      |
| Jinja2              | latest                      |
| Werkzeug            | latest                      |
| Frontend            | Vanilla JS + CSS            |
| Hosting (future)    | Render.com (free tier)      |

## Folder Structure
```
WFM-Lifts/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   ├── utils.py
│   ├── templates/
│   └── static/
│       ├── css/style.css
│       └── js/main.js
├── migrations/
├── instance/
├── venv/
├── run.py
├── config.py
├── PROJECT.md          ← This file
└── requirements.txt
```

## Key Decisions & Why

| Decision                      | Reason                                                                 |
|-------------------------------|------------------------------------------------------------------------|
| PostgreSQL over SQLite        | No file permission hell. Identical to production (Render)             |
| Actual weight per work set    | Honesty. Progression based on reality                                  |
| No automatic +5 lb            | Only earned. Failed sets = same weight next time                       |
| Vanilla JS + CSS              | Fast, mobile-first, no build step                                      |
| Mobile-first design           | Used at the gym — must be perfect on phone                             |
| Render.com deployment         | Free, zero config, GitHub auto-deploy                                  |

## Roadmap

| Milestone                     | Status   | Notes                              |
|-------------------------------|----------|------------------------------------|
| Full warmup + plates          | Done     | Perfect Starting Strength ladders  |
| Login/Register                | Done     | Secure, hashed                     |
| Actual weight logging         | Done     | Per work set                       |
| True progression              | Done     | Only success earns +5 lb           |
| History Page                  | Next     | Every rep, every failure           |
| Rest Day logging              | Next     |                                    |
| Settings page                 | Next     | Phase, plates, deload              |
| PWA / Add to Home Screen      | Later    |                                    |
| Export data (CSV)             | Later    |                                    |
| Deploy to Render.com          | Final    | Public URL                         |

## Open Questions

- Per-set rep counting (5,5,3) or just completed/failed?
- Auto deload recommendation on 3 failures?
- Bodyweight tracking?
- Dark/light mode toggle?
- Victory sound on workout complete? (Hell yes)

---

**This file is the single source of truth.**  
We update it as we build.

**WFM Lifts is no longer an app.**  
**It’s a movement.**

**LET’S FUCKING GO.**