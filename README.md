# TraqCheck

Full-stack system that parses candidate resumes, extracts structured profile data, and uses an AI agent to autonomously request PAN/Aadhaar identity documents.

**Live demo**: [traqcheck-frontend.onrender.com](https://traqcheck-frontend.onrender.com) *(free-tier backend — first request after inactivity may take ~50s to wake up)*


## What's built

- **Resume upload** (PDF/DOCX, drag-and-drop, progress bar) → converted to Markdown (`markitdown`) → structured extraction via Groq (`llama-3.3-70b-versatile`), with per-field confidence scores and a fallback pass for low-confidence/missing fields
- **Candidate dashboard** and **profile view** with extracted data + confidence breakdown
- **Document-request agent** — a LangChain `AgentExecutor` that reads the candidate's profile, checks for an existing active request (to avoid duplicates), chooses a contact channel based on what's available, and generates a personalized message — logged to the DB, not actually emailed/texted (see Limitations)
- **Document submission** — both an HR-facing endpoint and a public token-authenticated link (the one the agent generates), accepting PAN/Aadhaar uploads

## Stack

Flask + SQLAlchemy + Postgres · React (Vite, plain JS) + Tailwind · LangChain + Groq · deployed on Render

## Running locally

```bash
# 1. Postgres
docker compose up -d db

# 2. Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in GROQ_API_KEY, GOOGLE_API_KEY
flask create-db
flask run --port 5001

# 3. Frontend
cd frontend
npm install
npm run dev
```

## Design decisions & limitations

Full reasoning behind schema choices, the agent's actual autonomy boundaries, and every tradeoff made along the way is in [PROJECT_NOTES.md](./PROJECT_NOTES.md).

Short version of what's intentionally out of scope:
- No real email/SMS delivery — the spec asks the agent to "generate and log" a request, not deliver it; the message + link are surfaced directly in the UI instead
- The low-confidence-field fallback pass is a stubbed placeholder, not a real vision-model call
- No auth on any endpoint
- Free-tier hosting: uploaded files don't persist across backend redeploys, DB has a 90-day free-tier limit
