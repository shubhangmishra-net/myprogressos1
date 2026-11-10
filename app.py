der) VALUES(?,?,?)",
                default_habits,
            )
        if conn.execute("SELECT COUNT(*) FROM weekly_goals").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO weekly_goals(title,detail,start_date,end_date,status,created_at) VALUES(?,?,?,?,?,?)",
                [
                    ("Follow my planned workout and recovery routine", "Keep the week balanced; include recovery and adjust for sleep, soreness or school demands.", "2026-11-09", "2026-11-15", "In progress", now_text()),
                    ("Practise SMART goal planning", "Practise writing and reviewing one clear SMART goal each day from November 9 to November 12.", "2026-11-09", "2026-11-12", "In progress", now_text()),
                ],
            )
        if conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 0:
            projects = [
                ("Rylo manuscript — Chapter 8", "Writing", "In progress", "Resume from page 101; draft the next scene", "The Facility, the Fates, Camp Abstract and the pendrive thread.", now_text()),
                ("MIT Computational Data Science in Physics", "Learning", "In progress", "Continue the current lesson and capture one concept learned", "Track learning milestones rather than hours alone.", now_text()),
                ("TheLiterary main website", "Website", "Blocked", "Recover access to the existing main account", "The site still exists; it is locked/inaccessible because of account access issues. It is not destroyed.", now_text()),
                ("ShubhBooks promotional website", "Website", "In progress", "Review Search Console queries and page indexing", "Promotional site: shubhbooks.lovable.app.", now_text()),
                ("Calisthenics skill progression", "Fitness", "In progress", "Follow a balanced, supervised plan and allow recovery", "Track skill practice and recovery; do not turn personal records into routine targets.", now_text()),
            ]
            conn.executemany(
                "INSERT INTO projects(name,area,status,next_action,notes,created_at) VALUES(?,?,?,?,?,?)",
                projects,
            )
        if conn.execute("SELECT COUNT(*) FROM milestones").fetchone()[0] == 0:
            milestones = [
                ("Tuck L-sit — 10 seconds", "2026-11-09", "Calisthenics", "User-reported skill milestone."),
                ("Frogstand and advanced frogstand", "2026-11-09", "Calisthenics", "User-reported skill milestones."),
                ("Unassisted crow pose", "2026-11-09", "Calisthenics", "User-reported skill milestone."),
                ("Tuck front lever", "2026-11-07", "Calisthenics", "User-reported skill milestone."),
                ("Elbow lever", "2026-11-09", "Calisthenics", "User-reported skill milestone."),
            ]
            milestones.append(("Implementation backlog baseline: 2 of 4 goals completed", "2026-11-10", "Planning", "Two goals completed; two were still outstanding when the tracker was discussed."))
            conn.executemany(
                "INSERT INTO milestones(name,achieved_on,category,notes) VALUES(?,?,?,?)",
                milestones,
            )


def rows(query: str, params: tuple = ()) -> list[sqlite3.Row]:
    with db() as conn:
        return conn.execute(query, params).fetchall()


def one(query: str, params: tuple = ()) -> sqlite3.Row | None:
    with db() as conn:
        return conn.execute(query, params).fetchone()


def run(query: str, params: tuple = ()) -> int:
    with db() as conn:
        cur = conn.execute(query, params)
        return int(cur.lastrowid or 0)


def now_text() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def save_habit_status(habit_id: int, log_date: date, status: str) -> None:
    run(
        """INSERT INTO habit_logs(habit_id,log_date,status) VALUES(?,?,?)
           ON CONFLICT(habit_id,log_date) DO UPDATE SET status=excluded.status""",
        (habit_id, log_date.isoformat(), status),
    )


def save_habit_checkbox(habit_id: int, log_date: date, key: str) -> None:
    status = "Done" if st.session_state.get(key, False) else "Not done"
    save_habit_status(habit_id, log_date, status)


def status_badge(status: str) -> str:
    return {
        "Done": "✅",
        "Completed": "✅",
        "In progress": "🟦",
        "Planned": "🕓",
        "Partial": "🟨",
        "Rescheduled": "↪️",
        "Not started": "⚪",
        "Blocked": "⛔",
        "Skipped": "—",
    }.get(status, "•")


def metric_counts() -> tuple[int, int, int]:
    week_start = TODAY - timedelta(days=TODAY.weekday())
    week_end = week_start + timedelta(days=6)
    active = one(
        "SELECT COUNT(*) AS n FROM weekly_goals WHERE end_date>=? AND start_date<=? AND status!='Done'",
        (week_start.isoformat(), week_end.isoformat()),
    )["n"]
    today_goals = one(
        "SELECT COUNT(*) AS n FROM daily_goals WHERE goal_date=?",
        (TODAY.isoformat(),),
    )["n"]
    done_habits = one(
        "SELECT COUNT(*) AS n FROM habit_logs WHERE log_date=? AND status='Done'",
        (TODAY.isoformat(),),
    )["n"]
    return int(active), int(today_goals), int(done_habits)


def login_gate() -> bool:
    configured = os.getenv("PLANNER_PASSWORD", "")
    if not configured:
        st.error("Planner password is not configured yet.")
        st.markdown(
            "Add a secret named `PLANNER_PASSWORD` in your hosting provider's Secrets settings. "
            "For local testing, copy `.env.example` to `.env` and set a private password. "
            "Do not share the password in chat or commit it to your project."
        )
        return False
    if st.session_state.get("authenticated"):
        return True
    st.markdown("<div class='hero'><div class='smallcaps'>Private workspace</div><h1>My Progress OS</h1><p class='muted'>A calm place for goals, projects and progress.</p></div>", unsafe_allow_html=True)
    with st.form("login_form"):
        password = st.text_input("Planner password", type="pas