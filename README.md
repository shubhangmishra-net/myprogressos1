# My Progress OS

A private, light-theme Python productivity planner built with Streamlit and SQLite.

## Features
- Password gate for a single private workspace
- Dashboard for today's focus and active weekly goals
- SMART goal capture and persistent status updates
- Daily habit checkboxes saved immediately to SQLite
- Workout, recovery and skill milestone logs
- Project tracker seeded with the user's known projects
- Weekly review and optional OpenAI-powered planning summary
- SQLite and JSON backups

## Run locally

1. Install Python 3.10 or newer.
2. Create a virtual environment and install requirements:

   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\\Scripts\\Activate.ps1
   # macOS/Linux:
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and set a private `PLANNER_PASSWORD`.
4. Start the app:

   ```bash
   streamlit run app.py
   ```

The database is created at `data/planner.db` by default. Set `PLANNER_DB_PATH` or `PLANNER_DATA_DIR` to choose a different location.

## Deploy on Replit

1. Create a new Python Replit project and upload/import this project folder.
2. In **Secrets**, set `PLANNER_PASSWORD` to a long, unique password. Never put this value in the source code or chat.
3. Optionally set `OPENAI_API_KEY` and `OPENAI_MODEL` if AI review is wanted. The app works without an OpenAI key.
4. Use the run command in `.replit` to preview the app.
5. Before publishing, configure storage that persists across deployments/restarts. SQLite is a file database; if the deployment's filesystem is ephemeral, the data file may be reset. Set `PLANNER_DB_PATH` to a persistent mounted path if your selected hosting plan supports it, or switch to a hosted database before relying on it.
6. Verify persistence by creating a test goal, restarting/redeploying, and checking that it remains. Download a backup from **Settings & backups** before updates.

## Security and privacy
- Keep the deployment private and share the URL only with trusted people.
- Because this planner contains personal school and activity information, have a parent/guardian help manage the hosting account, password and any billing/API settings.
- Store API keys only in Replit Secrets or another hosting secrets manager.
- Optional AI review sends only the weekly task/project summary visible on the review page to OpenAI. Do not enter sensitive personal or health information into project notes.
- No private emotional journal is included; the app is for goals, projects, and activity logs.

## Notes
- The first launch seeds a few project names and skill milestones based on the requested planner context. It does not create or prescribe a workout plan.
- The user can edit projects, add goals, and customise habits within the app.
