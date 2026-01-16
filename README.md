# WFM Lifts — Starting Strength Progression Tracker

**"No fake gains. Only truth."**

A mobile-first, brutally honest Starting Strength progression app. You log what you actually lift — not what you wish you lifted. Progression is earned, not automatic.

## 🚀 Quick Start (Docker)

This project is fully containerized for easy development and database operations.

### Build the Image
```bash
docker build -t wfm-lifts .
```

### Run Locally
```bash
docker run --rm -p 5000:5000 --env-file .env wfm-lifts
```

## 📦 Database Migration (Supabase)

The app uses Supabase for persistent PostgreSQL hosting. 

### Export Data (Dump)
```bash
docker run --rm --env-file .env -v ${PWD}:/app wfm-lifts python scripts/dump_db.py
```

### Import Data (Restore)
```bash
docker run --rm -i --env-file .env -v ${PWD}:/app wfm-lifts python scripts/restore_db.py
```

## 🛠 Tech Stack
- **Backend:** Flask, SQLAlchemy, migrations
- **Database:** Supabase (PostgreSQL)
- **Frontend:** Vanilla JS, CSS (Mobile-First)
- **Infrastructure:** Docker, Render.com

## 📝 Rules of the Program
- **Progression:** +5 lb only on SUCCESS (all reps/sets).
- **Failure:** Stay at the same weight next session.
- **Warmups:** Automatic perfect plate math.

---
See `PROJECT.md` for full logic and technical details.
