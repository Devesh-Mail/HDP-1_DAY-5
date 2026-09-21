import sqlite3
from pathlib import Path

# ==========================================
# DATABASE LOCATION
# ==========================================

DB_PATH = (
    Path(__file__).resolve().parent
    / "students.db"
)

# ==========================================
# STUDENT DATA
# ==========================================

students = [
    (
        "22CS045",
        "Dhanushya",
        "Computer Science",
        85,
        72,
        90,
        78
    ),
    (
        "22CS046",
        "Rahul",
        "Computer Science",
        65,
        70,
        68,
        72
    ),
    (
        "22CS047",
        "Priya",
        "Information Technology",
        92,
        88,
        95,
        90
    ),
    (
        "22CS048",
        "Arun",
        "Information Technology",
        55,
        60,
        58,
        62
    ),
    (
        "22CS049",
        "Meena",
        "Computer Science",
        78,
        85,
        80,
        88
    )
]

# ==========================================
# CREATE DATABASE
# ==========================================

with sqlite3.connect(DB_PATH) as conn:

    # Delete old table if it exists

    conn.execute(
        "DROP TABLE IF EXISTS students"
    )

    # Create table

    conn.execute(
        """
        CREATE TABLE students (

            student_id TEXT PRIMARY KEY,

            name TEXT NOT NULL,

            department TEXT NOT NULL,

            python INTEGER NOT NULL,

            database INTEGER NOT NULL,

            ai INTEGER NOT NULL,

            web INTEGER NOT NULL

        )
        """
    )

    # Insert students

    conn.executemany(
        """
        INSERT INTO students
        (
            student_id,
            name,
            department,
            python,
            database,
            ai,
            web
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        students
    )


print(
    f"Database created successfully:"
    f"\n{DB_PATH}"
)

print(
    f"Inserted {len(students)} students."
)