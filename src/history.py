"""
history.py — Persistent drift history using SQLite.

Stores drift check results over time for trend analysis
and historical tracking.
"""

import os
import sqlite3
from datetime import datetime, timezone

from logger import get_logger

logger = get_logger(__name__)

# Database file path
DB_DIR = os.getenv("DB_DIR", "data")
DB_PATH = os.path.join(DB_DIR, "drift_history.db")


def _get_connection():
    """Get a SQLite connection, creating the database and table if needed."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS drift_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                features_drifted INTEGER NOT NULL,
                avg_drift_score REAL NOT NULL,
                accuracy_drop REAL NOT NULL,
                severity TEXT NOT NULL
            )
        """)
    return conn


def save_drift_result(result):
    """
    Save a drift detection result to the history database.

    Args:
        result: Dict containing drift results and impact data.
            Expected keys:
                - drift_results: Dict of feature→drift info
                - accuracy_drop: float
    """
    conn = None
    try:
        drift_results = result.get("drift_results", {})
        accuracy_drop = result.get("accuracy_drop", 0.0)

        # Count drifted features
        drifted = [f for f, r in drift_results.items() if r.get("drift_detected", False)]
        features_drifted = len(drifted)

        # Calculate average drift score
        scores = [r.get("drift_score", 0) for r in drift_results.values()]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # Determine overall severity
        if avg_score > 0.3:
            severity = "high"
        elif avg_score > 0.1:
            severity = "medium"
        else:
            severity = "low"

        timestamp = datetime.now(timezone.utc).isoformat()

        conn = _get_connection()
        with conn:
            conn.execute(
                """
                INSERT INTO drift_history
                    (timestamp, features_drifted, avg_drift_score, accuracy_drop, severity)
                VALUES (?, ?, ?, ?, ?)
                """,
                (timestamp, features_drifted, avg_score, accuracy_drop, severity),
            )

        logger.info(
            "Saved drift result: drifted=%d, avg_score=%.4f, severity=%s",
            features_drifted,
            avg_score,
            severity,
        )

    except Exception as e:
        logger.error("Failed to save drift result: %s", e)
    finally:
        if conn:
            conn.close()


def get_drift_history(limit=50):
    """
    Retrieve the most recent drift check results.

    Args:
        limit: Maximum number of records to return (default 50).

    Returns:
        List of dicts with drift history records.
    """
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.execute(
            """
            SELECT id, timestamp, features_drifted, avg_drift_score,
                   accuracy_drop, severity
            FROM drift_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = [dict(row) for row in cursor.fetchall()]
        logger.info("Retrieved %d drift history records", len(rows))
        return rows

    except Exception as e:
        logger.error("Failed to retrieve drift history: %s", e)
        return []
    finally:
        if conn:
            conn.close()


def get_drift_trend():
    """
    Get daily average drift scores for trend analysis.

    Returns:
        List of dicts with date and avg_drift_score.
    """
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.execute("""
            SELECT
                DATE(timestamp) as date,
                AVG(avg_drift_score) as avg_drift_score,
                AVG(accuracy_drop) as avg_accuracy_drop,
                COUNT(*) as check_count
            FROM drift_history
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 30
            """)
        rows = [dict(row) for row in cursor.fetchall()]
        logger.info("Retrieved %d daily trend records", len(rows))
        return rows

    except Exception as e:
        logger.error("Failed to retrieve drift trend: %s", e)
        return []
    finally:
        if conn:
            conn.close()
