# My Progress OS — Replit Agent notes

Keep this project as a Python Streamlit application. Do not convert it to a JavaScript-only app.

## Required behavior
- Preserve the light, minimalist interface.
- Preserve SQLite persistence and keep all database writes server-side.
- The user wants checkboxes/status changes to persist across reruns and restarts.
- Keep the password gate. Never remove it to make preview/deployment easier.
- Keep OpenAI features optional. The app must work without `OPENAI_API_KEY`.
- Never hard-code or print secrets. Read secrets only from environment variables.
- AI review may summarize only non-sensitive task/project progress; do not send personal journal or health information to AI.
- Keep backup downloads available.

## Run
`streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true`

For deployment, use the platform-provided `$PORT` in the run command.

## Data persistence
The default SQLite file is `data/planner.db`. Set `PLANNER_DB_PATH` to a writable persistent storage location for deployments. Before calling a deployment complete, verify that a test goal survives an app restart and a redeployment. Do not claim persistence until verified.

## Safety and privacy
This is a single-user personal planner. Keep it password-protected and do not publish personal records or secrets. Ask before changing the database schema in a way that could discard data. Back up the database before migrations.
