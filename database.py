
import sqlite3
from pathlib import Path

# Store the database in the project folder
DATABASE_PATH = Path(__file__).resolve().parent / "clouddeploy.db"


def get_connection():
    """Create a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the deployments table if it does not exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS deployments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                environment TEXT NOT NULL DEFAULT 'local',
                status TEXT NOT NULL DEFAULT 'pending',
                details TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def add_deployment(
    version,
    environment="local",
    status="success",
    details=""
):
    """Save a deployment record and return its ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO deployments
                (version, environment, status, details)
            VALUES (?, ?, ?, ?)
            """,
            (version, environment, status, details),
        )
        return cursor.lastrowid


def get_deployments(limit=20):
    """Return the most recent deployment records."""
    limit = max(1, min(int(limit), 100))

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, version, environment, status, details, created_at
            FROM deployments
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [dict(row) for row in rows]


if __name__ == "__main__":
    initialize_database()
    print("CloudDeploy database initialized successfully.")

    deployment_id = add_deployment(
        version="v1-test",
        environment="local",
        status="success",
        details="Database test completed",
    )

    print(f"Test deployment saved with ID: {deployment_id}")
    print("Recent deployments:")
    for deployment in get_deployments():
        print(deployment)