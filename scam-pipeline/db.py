"""
SQLite database layer.
Tables: news_events, event_analysis, generated_cases, user_feedback
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional

from config import DB_PATH


def _to_str(val) -> str:
    """Ensure a value is a string; JSON-encode lists/dicts."""
    if isinstance(val, (list, dict)):
        return json.dumps(val, ensure_ascii=False)
    return str(val) if val else ""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS news_events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT,
                source      TEXT,
                url         TEXT UNIQUE,
                published_at TEXT,
                raw_text    TEXT,
                summary     TEXT,
                keyword_score INTEGER DEFAULT 0,
                created_at  TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS event_analysis (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id              INTEGER NOT NULL,
                scam_potential       TEXT,
                reason               TEXT,
                impersonation_targets TEXT,
                likely_channels      TEXT,
                likely_actions       TEXT,
                scam_angles          TEXT,
                seasonality          TEXT,
                created_at           TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(news_id) REFERENCES news_events(id)
            );

            CREATE TABLE IF NOT EXISTS generated_cases (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id             INTEGER NOT NULL,
                title               TEXT,
                event_hook          TEXT,
                impersonated_entity TEXT,
                scam_goal           TEXT,
                likely_channel      TEXT,
                red_flags           TEXT,
                safe_response       TEXT,
                embedding_id        TEXT,
                created_at          TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(news_id) REFERENCES news_events(id)
            );

            CREATE TABLE IF NOT EXISTS user_feedback (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id        INTEGER,
                user_input     TEXT,
                feedback_label TEXT,
                notes          TEXT,
                created_at     TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(case_id) REFERENCES generated_cases(id)
            );
        """)


# ── news_events CRUD ──────────────────────────────────────────────

def insert_news(title: str, source: str, url: str,
                published_at: str, raw_text: str,
                summary: str = "", keyword_score: int = 0) -> Optional[int]:
    with get_conn() as conn:
        try:
            cur = conn.execute(
                """INSERT INTO news_events
                   (title, source, url, published_at, raw_text, summary, keyword_score)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (title, source, url, published_at, raw_text, summary, keyword_score),
            )
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return None


def get_news_by_id(news_id: int) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM news_events WHERE id = ?", (news_id,)
        ).fetchone()
        return dict(row) if row else None


def get_unanalyzed_news(min_score: int = 3) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT n.* FROM news_events n
               LEFT JOIN event_analysis a ON n.id = a.news_id
               WHERE a.id IS NULL AND n.keyword_score >= ?
               ORDER BY n.keyword_score DESC""",
            (min_score,),
        ).fetchall()
        return [dict(r) for r in rows]


# ── event_analysis CRUD ───────────────────────────────────────────

def insert_analysis(news_id: int, analysis: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO event_analysis
               (news_id, scam_potential, reason, impersonation_targets,
                likely_channels, likely_actions, scam_angles, seasonality)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                news_id,
                analysis.get("scam_potential", ""),
                analysis.get("reason", ""),
                json.dumps(analysis.get("impersonation_targets", []), ensure_ascii=False),
                json.dumps(analysis.get("likely_channels", []), ensure_ascii=False),
                json.dumps(analysis.get("likely_actions", []), ensure_ascii=False),
                json.dumps(analysis.get("scam_angles", []), ensure_ascii=False),
                analysis.get("seasonality", ""),
            ),
        )
        return cur.lastrowid


def get_analysis_by_news_id(news_id: int) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM event_analysis WHERE news_id = ?", (news_id,)
        ).fetchone()
        return dict(row) if row else None


# ── generated_cases CRUD ──────────────────────────────────────────

def insert_case(news_id: int, case: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO generated_cases
               (news_id, title, event_hook, impersonated_entity,
                scam_goal, likely_channel, red_flags, safe_response)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                news_id,
                _to_str(case.get("title", "")),
                _to_str(case.get("event_hook", "")),
                _to_str(case.get("impersonated_entity", "")),
                _to_str(case.get("scam_goal", "")),
                _to_str(case.get("likely_channel", "")),
                json.dumps(case.get("red_flags", []), ensure_ascii=False),
                _to_str(case.get("safe_response", "")),
            ),
        )
        return cur.lastrowid


def update_case_embedding(case_id: int, embedding_id: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE generated_cases SET embedding_id = ? WHERE id = ?",
            (embedding_id, case_id),
        )


# ── user_feedback CRUD ────────────────────────────────────────────

def insert_feedback(case_id: int, user_input: str,
                    feedback_label: str, notes: str = "") -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO user_feedback
               (case_id, user_input, feedback_label, notes)
               VALUES (?, ?, ?, ?)""",
            (case_id, user_input, feedback_label, notes),
        )
        return cur.lastrowid


# ── Stats ─────────────────────────────────────────────────────────

def get_stats() -> dict:
    with get_conn() as conn:
        stats = {}
        for table in ["news_events", "event_analysis", "generated_cases", "user_feedback"]:
            row = conn.execute(f"SELECT COUNT(*) as cnt FROM {table}").fetchone()
            stats[table] = row["cnt"]
        return stats


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
    print(get_stats())
