import sqlite3
import os
import json
import time
import glob
from typing import List, Dict, Any

class SessionMemory:
    def __init__(self, session_id: str, max_window_messages: int = 10, db_dir: str = "~/.tiny-agent/sessions"):
        self.session_id = session_id
        self.max_window_messages = max_window_messages
        self.db_dir = os.path.expanduser(db_dir)
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_path = os.path.join(self.db_dir, f"{session_id}.db")
        self._init_db()
        self.window: List[Dict[str, Any]] = []

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    role TEXT,
                    content TEXT,
                    short_content TEXT
                )
            ''')
            conn.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
                    content, short_content, content="messages", content_rowid="id"
                )
            ''')
            conn.execute('''
                CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
                  INSERT INTO messages_fts(rowid, content, short_content) VALUES (new.id, new.content, new.short_content);
                END;
            ''')
            conn.execute('''
                CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
                  INSERT INTO messages_fts(messages_fts, rowid, content, short_content) VALUES('delete', old.id, old.content, old.short_content);
                END;
            ''')
            conn.execute('''
                CREATE TRIGGER IF NOT EXISTS messages_au AFTER UPDATE ON messages BEGIN
                  INSERT INTO messages_fts(messages_fts, rowid, content, short_content) VALUES('delete', old.id, old.content, old.short_content);
                  INSERT INTO messages_fts(rowid, content, short_content) VALUES (new.id, new.content, new.short_content);
                END;
            ''')

    def add_message(self, message: Dict[str, Any]):
        self.window.append(message)
        if len(self.window) > self.max_window_messages:
            spilled = self.window.pop(0)
            self._spill_to_db(spilled)

    def _spill_to_db(self, message: Dict[str, Any]):
        content_val = message.get("content", "")
        content_str = json.dumps(content_val) if not isinstance(content_val, str) else content_val
        short_content = content_str[:100] + "..." if len(content_str) > 100 else content_str
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (timestamp, role, content, short_content) VALUES (?, ?, ?, ?)",
                (time.time(), message.get("role", "unknown"), content_str, short_content)
            )

    def get_window(self) -> List[Dict[str, Any]]:
        return self.window

    def list_archived_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT id, timestamp, role, short_content FROM messages ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    def get_archived_message(self, msg_id: int) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM messages WHERE id = ?", (msg_id,)).fetchone()
            return dict(row) if row else {}

    @classmethod
    def search_past_sessions(cls, query: str, limit: int = 20, db_dir: str = "~/.tiny-agent/sessions") -> List[Dict[str, Any]]:
        db_dir = os.path.expanduser(db_dir)
        results = []
        for db_file in glob.glob(os.path.join(db_dir, "*.db")):
            session_id = os.path.basename(db_file).replace('.db', '')
            try:
                with sqlite3.connect(db_file) as conn:
                    conn.row_factory = sqlite3.Row
                    rows = conn.execute('''
                        SELECT m.id, m.timestamp, m.role, m.short_content 
                        FROM messages m 
                        JOIN messages_fts f ON m.id = f.rowid 
                        WHERE messages_fts MATCH ? 
                        ORDER BY rank LIMIT ?
                    ''', (query, limit)).fetchall()
                    for r in rows:
                        d = dict(r)
                        d['session_id'] = session_id
                        results.append(d)
            except Exception:
                pass
        return sorted(results, key=lambda x: x['timestamp'], reverse=True)[:limit]

    @classmethod
    def cleanup_old_sessions(cls, days_old: int = 7, db_dir: str = "~/.tiny-agent/sessions"):
        db_dir = os.path.expanduser(db_dir)
        cutoff = time.time() - (days_old * 86400)
        for db_file in glob.glob(os.path.join(db_dir, "*.db")):
            if os.path.getmtime(db_file) < cutoff:
                try:
                    os.remove(db_file)
                except Exception:
                    pass
