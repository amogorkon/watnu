from PyQt6.QtSql import QSqlQuery
from classes import iter_over
from classes import submit_sql

query = submit_sql(
    f"""
SELECT id, deadline FROM tasks
WHERE deadline != "Infinity";
"""
)

for row in iter_over(query):
    deadline_query = submit_sql(
        f"""
INSERT OR IGNORE INTO deadlines
(task_id, time_of_reference)
VALUES ({row(0)}, {row(1)})
		"""
    )


import sys

sys.exit()
