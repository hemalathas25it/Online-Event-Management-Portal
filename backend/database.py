import sqlite3
import os
from datetime import datetime, date
from typing import List, Optional, Dict, Any

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "events.db"))


def get_connection() -> sqlite3.Connection:
    """Provide a SQLite connection with WAL mode and row factory."""
    conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Initialize database tables and seed initial data if empty."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL
            );
        """)

        # Events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                date TEXT NOT NULL,
                location TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );
        """)

        # Registrations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                user_id INTEGER,
                participant_name TEXT NOT NULL,
                registered_at TEXT NOT NULL,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                UNIQUE(event_id, participant_name)
            );
        """)

        conn.commit()

    seed_data()


def seed_data() -> None:
    """Seed initial administrator, users, events, and registrations if not present."""
    from backend.auth import hash_password

    now_iso = datetime.now().isoformat()

    with get_connection() as conn:
        cursor = conn.cursor()

        # Seed Admin user if not exists
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                ("admin", hash_password("admin123"), "admin", now_iso),
            )

        # Seed regular user if not exists
        cursor.execute("SELECT id FROM users WHERE username = 'student01'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                ("student01", hash_password("student123"), "user", now_iso),
            )

        # Seed events if none exist
        cursor.execute("SELECT COUNT(*) as count FROM events")
        event_count = cursor.fetchone()["count"]
        if event_count == 0:
            sample_events = [
                (
                    "Annual Tech Symposium 2026",
                    "A gathering of tech enthusiasts, researchers, and developers featuring keynotes and project exhibits.",
                    "2026-10-15",
                    "Main Auditorium, Tech Campus",
                    now_iso,
                ),
                (
                    "Student Event Management Workshop",
                    "Practical hands-on workshop on event coordination, budgeting, and team leadership.",
                    "2026-10-28",
                    "Seminar Hall B",
                    now_iso,
                ),
                (
                    "National Hackathon 2026",
                    "36-hour competitive coding hackathon addressing real-world civic challenges.",
                    "2026-11-10",
                    "Innovation Center",
                    now_iso,
                ),
                (
                    "College Cultural Fest",
                    "Grand inter-college cultural festival featuring music, dance, theater, and arts.",
                    "2026-12-05",
                    "Campus Open Grounds",
                    now_iso,
                ),
                (
                    "Web Development Bootcamp",
                    "Comprehensive fast-track course on building modern web applications.",
                    "2026-06-18",
                    "Computer Lab 3",
                    now_iso,
                ),
                (
                    "Orientation & Career Guidance Seminar",
                    "Introductory career readiness session for incoming students and freshers.",
                    "2026-07-22",
                    "Convention Center",
                    now_iso,
                ),
            ]
            cursor.executemany(
                "INSERT INTO events (title, description, date, location, created_at) VALUES (?, ?, ?, ?, ?)",
                sample_events,
            )

            # Seed sample registrations
            cursor.execute("SELECT id, title FROM events LIMIT 2")
            rows = cursor.fetchall()
            if rows:
                ev1_id = rows[0]["id"]
                ev2_id = rows[1]["id"]
                cursor.execute("SELECT id FROM users WHERE username = 'student01'")
                student = cursor.fetchone()
                student_id = student["id"] if student else None

                cursor.execute(
                    "INSERT OR IGNORE INTO registrations (event_id, user_id, participant_name, registered_at) VALUES (?, ?, ?, ?)",
                    (ev1_id, student_id, "Alex Johnson", now_iso),
                )
                cursor.execute(
                    "INSERT OR IGNORE INTO registrations (event_id, user_id, participant_name, registered_at) VALUES (?, ?, ?, ?)",
                    (ev1_id, None, "Sarah Miller", now_iso),
                )
                cursor.execute(
                    "INSERT OR IGNORE INTO registrations (event_id, user_id, participant_name, registered_at) VALUES (?, ?, ?, ?)",
                    (ev2_id, student_id, "Alex Johnson", now_iso),
                )

        conn.commit()


# --- User Helpers ---

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, role, created_at FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, role, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_user(username: str, password_hash: str, role: str = "user") -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        created_at = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            (username, password_hash, role, created_at),
        )
        user_id = cursor.lastrowid
        conn.commit()
        return {"id": user_id, "username": username, "role": role, "created_at": created_at}


def get_all_users(search: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        if search:
            query = "SELECT id, username, role, created_at FROM users WHERE username LIKE ? ORDER BY id DESC"
            cursor.execute(query, (f"%{search}%",))
        else:
            cursor.execute("SELECT id, username, role, created_at FROM users ORDER BY id DESC")
        return [dict(r) for r in cursor.fetchall()]


# --- Event Helpers ---

def get_all_events(filter_type: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    today_str = date.today().isoformat()
    query = """
        SELECT e.id, e.title, e.description, e.date, e.location, e.created_at,
               COUNT(r.id) as participant_count
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
    """
    conditions = []
    params = []

    if filter_type == "upcoming":
        conditions.append("e.date >= ?")
        params.append(today_str)
    elif filter_type == "past":
        conditions.append("e.date < ?")
        params.append(today_str)

    if search:
        conditions.append("(e.title LIKE ? OR e.description LIKE ? OR e.location LIKE ?)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY e.id"

    if filter_type == "past":
        query += " ORDER BY e.date DESC"
    else:
        query += " ORDER BY e.date ASC"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["is_upcoming"] = (d["date"] >= today_str)
            result.append(d)
        return result


def get_event_by_id(event_id: int) -> Optional[Dict[str, Any]]:
    today_str = date.today().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id, e.title, e.description, e.date, e.location, e.created_at,
                   COUNT(r.id) as participant_count
            FROM events e
            LEFT JOIN registrations r ON e.id = r.event_id
            WHERE e.id = ?
            GROUP BY e.id
        """, (event_id,))
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        d["is_upcoming"] = (d["date"] >= today_str)
        return d


def create_event(title: str, description: str, date_str: str, location: str) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        created_at = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO events (title, description, date, location, created_at) VALUES (?, ?, ?, ?, ?)",
            (title, description, date_str, location, created_at),
        )
        event_id = cursor.lastrowid
        conn.commit()
        return get_event_by_id(event_id)


def update_event(event_id: int, title: str, description: str, date_str: str, location: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE events SET title = ?, description = ?, date = ?, location = ? WHERE id = ?",
            (title, description, date_str, location, event_id),
        )
        if cursor.rowcount == 0:
            return None
        conn.commit()
        return get_event_by_id(event_id)


def delete_event(event_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        return deleted


# --- Registration Helpers ---

def get_all_registrations(search: Optional[str] = None, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    query = """
        SELECT r.id, r.event_id, r.user_id, r.participant_name, r.registered_at,
               e.title as event_title, e.date as event_date, e.location as event_location,
               u.username as registered_by_user
        FROM registrations r
        JOIN events e ON r.event_id = e.id
        LEFT JOIN users u ON r.user_id = u.id
    """
    conditions = []
    params = []

    if user_id is not None:
        conditions.append("r.user_id = ?")
        params.append(user_id)

    if search:
        conditions.append("(r.participant_name LIKE ? OR e.title LIKE ? OR u.username LIKE ?)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY r.id DESC"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]


def get_registration_by_id(reg_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.event_id, r.user_id, r.participant_name, r.registered_at,
                   e.title as event_title, e.date as event_date
            FROM registrations r
            JOIN events e ON r.event_id = e.id
            WHERE r.id = ?
        """, (reg_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def check_registration_exists(event_id: int, participant_name: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM registrations WHERE event_id = ? AND LOWER(participant_name) = LOWER(?)",
            (event_id, participant_name.strip()),
        )
        return cursor.fetchone() is not None


def create_registration(event_id: int, participant_name: str, user_id: Optional[int] = None) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        registered_at = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO registrations (event_id, user_id, participant_name, registered_at) VALUES (?, ?, ?, ?)",
            (event_id, user_id, participant_name.strip(), registered_at),
        )
        reg_id = cursor.lastrowid
        conn.commit()
        return get_registration_by_id(reg_id)


def delete_registration(reg_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM registrations WHERE id = ?", (reg_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        return deleted


# --- Dashboard & Reports Helpers ---

def get_dashboard_stats() -> Dict[str, int]:
    today_str = date.today().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM events WHERE date >= ?", (today_str,))
        upcoming_count = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM events WHERE date < ?", (today_str,))
        past_count = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM registrations")
        registration_count = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()["count"]

        return {
            "upcoming_events": upcoming_count,
            "past_events": past_count,
            "total_registrations": registration_count,
            "total_users": user_count,
        }


def get_dashboard_reports() -> Dict[str, Any]:
    today_str = date.today().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()

        # Event-wise registration distribution
        cursor.execute("""
            SELECT e.id, e.title, e.date,
                   (CASE WHEN e.date >= ? THEN 'Upcoming' ELSE 'Past' END) as status,
                   COUNT(r.id) as participant_count
            FROM events e
            LEFT JOIN registrations r ON e.id = r.event_id
            GROUP BY e.id
            ORDER BY participant_count DESC, e.date DESC
        """, (today_str,))
        event_distribution = [dict(r) for r in cursor.fetchall()]

        # Recent registrations
        cursor.execute("""
            SELECT r.id, r.participant_name, r.registered_at, e.title as event_title
            FROM registrations r
            JOIN events e ON r.event_id = e.id
            ORDER BY r.id DESC
            LIMIT 5
        """)
        recent_registrations = [dict(r) for r in cursor.fetchall()]

        return {
            "event_distribution": event_distribution,
            "recent_registrations": recent_registrations,
        }
