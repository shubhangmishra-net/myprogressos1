from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
load_dotenv(APP_DIR / ".env")
DATA_DIR = Path(os.getenv("PLANNER_DATA_DIR", APP_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = Path(os.getenv("PLANNER_DB_PATH", DATA_DIR / "planner.db"))
TZ = ZoneInfo("Asia/Kolkata")
TODAY = datetime.now(TZ).date()

st.set_page_config(
    page_title="My Progress OS",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      :root { color-scheme: light; }
      .stApp { background: #f7f8fb; color: #1f2937; }
      [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e7eaf0; }
      [data-testid="stHeader"] { background: rgba(247,248,251,.88); }
      .block-container { max-width: 1180px; padding-top: 1.5rem; padding-bottom: 3rem; }
      .hero { background: linear-gradient(115deg,#ffffff,#eef4ff); border: 1px solid #e4eaf5; border-radius: 22px; padding: 1.35rem 1.5rem; margin-bottom: 1rem; }
      .muted { color: #64748b; font-size: .9rem; }
      .smallcaps { letter-spacing: .12em; text-transform: uppercase; color: #64748b; font-size: .72rem; font-weight: 700; }
      div[data-testid="stMetric"] { background: white; border: 1px solid #e8ebf1; padding: 14px 16px; border-radius: 16px; }
      div.stButton > button, div.stDownloadButton > button { border-radius: 10px; }
      .stTabs [data-baseweb="tab"] { height: 42px; }
      [data-testid="stForm"] { background: white; border: 1px solid #e8ebf1; padding: 1rem; border-radius: 16px; }
      .note { background: #fff; border: 1px solid #e8ebf1; padding: 12px 14px; border-radius: 14px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@contextmanager
def db() -> Any:
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS weekly_goals (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT NOT NULL,
              detail TEXT DEFAULT '',
              start_date TEXT NOT NULL,
              end_date TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'Not started',
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS daily_goals (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              goal_date TEXT NOT NULL,
              title TEXT NOT NULL,
              specific TEXT DEFAULT '',
              measurable TEXT DEFAULT '',
              achievable TEXT DEFAULT '',
              relevant TEXT DEFAULT '',
              time_bound TEXT DEFAULT '',
              planned_time TEXT DEFAULT '',
              status TEXT NOT NULL DEFAULT 'Planned',
              outcome TEXT DEFAULT '',
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS habits (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL UNIQUE,
              category TEXT DEFAULT 'Personal',
              active INTEGER NOT NULL DEFAULT 1,
              sort_order INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS habit_logs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              habit_id INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
              log_date TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'Done',
              note TEXT DEFAULT '',
              UNIQUE(habit_id, log_date)
            );
            CREATE TABLE IF NOT EXISTS workout_logs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              workout_date TEXT NOT NULL,
              activity TEXT NOT NULL,
              duration_minutes INTEGER,
              kind TEXT NOT NULL DEFAULT 'Training',
              notes TEXT DEFAULT '',
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS projects (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              area TEXT NOT NULL DEFAULT 'Personal',
              status TEXT NOT NULL DEFAULT 'In progress',
              next_action TEXT DEFAULT '',
              notes TEXT DEFAULT '',
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS milestones (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              achieved_on TEXT NOT NULL,
              category TEXT NOT NULL DEFAULT 'Skill',
              notes TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS reviews (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              week_start TEXT NOT NULL UNIQUE,
              went_well TEXT DEFAULT '',
              next_focus TEXT DEFAULT '',
              created_at TEXT NOT NULL
            );
            """
        )
        # Seed once, without overwriting the user's later edits.
        if conn.execute("SELECT COUNT(*) FROM habits").fetchone()[0] == 0:
            default_habits = [
                ("Review today's main goal", "Planning", 1),
                ("Reading", "Learning", 2),
                ("MIT course / focused study", "Learning", 3),
                ("Writing session", "Creative work", 4),
                ("Movement or planned recovery", "Well-being", 5),
            ]
            conn.executemany(
                "INSERT INTO habits(name, category, sort_or