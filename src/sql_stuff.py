import sqlite3

from configuration import Config

config: Config
db: sqlite3.Connection

query = db.execute(
    """
SELECT id, deadline FROM tasks
WHERE deadline != "Infinity";
"""
)

for task_id, deadline in query.fetchall():
    deadline_query = db.execute(
        f"""
INSERT OR IGNORE INTO deadlines
(task_id, time_of_reference)
VALUES ({task_id}, {deadline})
		"""
    )

db.commit()
