from classes import submit_sql

print("FIRST START")


def run(db, config):

    ### CREATE SQL TABLES ###
    # qsql can't handle multiple statements >:|

    statements = """
CREATE TABLE "activities" (
    "activity_id"	INTEGER NOT NULL UNIQUE,
    "name"	VARCHAR(255) NOT NULL UNIQUE,
    "adjust_time_spent"	INTEGER DEFAULT 0,
    PRIMARY KEY("activity_id" AUTOINCREMENT)
);
CREATE TABLE "constraints" (
    "flags"	TEXT NOT NULL DEFAULT 0,
    "task_id"	INTEGER NOT NULL,
    PRIMARY KEY("task_id"),
    FOREIGN KEY("task_id") REFERENCES "tasks"("id") ON DELETE CASCADE
);

CREATE TABLE "deadlines" (
    "deadline_id"	INTEGER NOT NULL UNIQUE,
    "task_id"	INTEGER NOT NULL,
    "time_of_reference"	REAL NOT NULL,
    PRIMARY KEY("deadline_id" AUTOINCREMENT),
    FOREIGN KEY("task_id") REFERENCES "tasks"("id") ON DELETE CASCADE
);

CREATE TABLE levels(
    level_id INTEGER PRIMARY KEY UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL UNIQUE
    );

CREATE TABLE "mantras" (
    "mantra_id"	INTEGER NOT NULL UNIQUE,
    "text"	TEXT NOT NULL UNIQUE,
    "last_time"	INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY("mantra_id" AUTOINCREMENT)
);

CREATE TABLE "repeats" (
    "repeat_id"	INTEGER NOT NULL UNIQUE,
    "task_id"	INTEGER NOT NULL,
    "every_ilk"	INTEGER NOT NULL DEFAULT -1,
    "x_every"	INTEGER NOT NULL,
    "x_per"	INTEGER NOT NULL,
    "per_ilk"	INTEGER NOT NULL DEFAULT -1,
    PRIMARY KEY("repeat_id" AUTOINCREMENT),
    FOREIGN KEY("task_id") REFERENCES "tasks"("id") on delete cascade
);

CREATE TABLE "resources" (
    "resource_id"	INTEGER NOT NULL UNIQUE,
    "url"	TEXT NOT NULL UNIQUE,
    PRIMARY KEY("resource_id" AUTOINCREMENT)
);

CREATE TABLE "sessions" (
    "session_id"	INTEGER NOT NULL UNIQUE,
    "task_id"	INTEGER NOT NULL,
    "start"	INTEGER NOT NULL,
    "stop"	INTEGER NOT NULL,
    "finished"	INTEGER NOT NULL DEFAULT 0,
    "pause_time"	INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY("task_id") REFERENCES "tasks"("id") ON DELETE CASCADE,
    PRIMARY KEY("session_id")
);

CREATE TABLE "skills" (
    "skill_id"	INTEGER NOT NULL UNIQUE,
    "name"	TEXT NOT NULL UNIQUE,
    PRIMARY KEY("skill_id" AUTOINCREMENT)
);

CREATE TABLE "spaces" (
    "space_id"	INTEGER NOT NULL UNIQUE,
    "name"	VARCHAR(255) NOT NULL UNIQUE,
    "priority"	REAL DEFAULT 0,
    "primary_activity_id"	INTEGER,
    "secondary_activity_id"	INTEGER,
    FOREIGN KEY("secondary_activity_id") REFERENCES "activities"("activity_id"),
    FOREIGN KEY("primary_activity_id") REFERENCES "activities"("activity_id"),
    PRIMARY KEY("space_id" AUTOINCREMENT)
);

CREATE TABLE "task_requires_task" (
      "task_of_concern"  INTEGER NOT NULL,
       "required_task"  INTEGER NOT NULL CHECK (task_of_concern <> required_task),
      FOREIGN KEY("task_of_concern") REFERENCES "tasks" ("id") ON DELETE CASCADE,
      FOREIGN KEY("required_task") REFERENCES "tasks" ("id") ON DELETE CASCADE
);

CREATE TABLE "task_trains_skill" (
    "task_id"	INTEGER NOT NULL,
    "skill_id"	INTEGER NOT NULL,
    PRIMARY KEY("task_id","skill_id"),
    FOREIGN KEY("task_id") REFERENCES "tasks" ON DELETE CASCADE,
    FOREIGN KEY("skill_id") REFERENCES "skills" ON DELETE CASCADE
) WITHOUT ROWID;

CREATE TABLE "task_uses_resource" (
    "task_id"	INTEGER NOT NULL,
    "resource_id"	INTEGER NOT NULL,
    PRIMARY KEY("task_id","resource_id"),
    FOREIGN KEY("task_id") REFERENCES "tasks"("id")
) WITHOUT ROWID;

CREATE TABLE "tasks" (
    "id"	INTEGER NOT NULL UNIQUE,
    "do"	VARCHAR(280) NOT NULL,
    "notes"	TEXT,
    "space_id"	INTEGER,
    "done"	INTEGER NOT NULL DEFAULT 0,
    "draft"	INTEGER NOT NULL DEFAULT 0,
    "inactive"	INTEGER NOT NULL DEFAULT 0,
    "deleted"	INTEGER NOT NULL DEFAULT 0,
    "priority"	REAL NOT NULL DEFAULT 0,
    "level_id"	INTEGER NOT NULL DEFAULT 0,
    "workload"	INTEGER,
    "difficulty"	REAL DEFAULT 5,
    "fear"	REAL DEFAULT 5,
    "embarassment"	REAL DEFAULT 5,
    "last_checked"	INTEGER DEFAULT 0,
    "time_spent"	INTEGER DEFAULT 0,
    "adjust_time_spent"	INTEGER DEFAULT 0,
    "ilk"	INTEGER NOT NULL DEFAULT 1,
    "primary_activity_id"	INTEGER,
    "secondary_activity_id"	INTEGER,
    "template"	INTEGER,
    FOREIGN KEY("template") REFERENCES "tasks"("id"),
    FOREIGN KEY("space_id") REFERENCES "spaces"("space_id") ON DELETE SET NULL,
    FOREIGN KEY("level_id") REFERENCES "spaces"("level_id") ON DELETE SET NULL,
    FOREIGN KEY("secondary_activity_id") REFERENCES "activities"("activity_id") ON DELETE SET NULL,
    FOREIGN KEY("primary_activity_id") REFERENCES "activities"("activity_id") ON DELETE SET NULL,
    PRIMARY KEY("id" AUTOINCREMENT)
)
"""

    for S in statements.split(";"):
        submit_sql(S)

    ### Default Entries ###

    for name, level_id in zip(["MUST NOT", "SHOULD NOT", "COULD", "SHOULD", "MUST"], [-2, -1, 0, 1, 2]):
        submit_sql(
            f"""
        INSERT INTO levels (name, level_id)
        VALUES ('{name}', {level_id})
        """
        )

    for name, activity_id in zip(["BODY", "SPIRIT", "MIND"], [0, 1, 2]):
        submit_sql(
            f"""
        INSERT INTO activities (name, activity_id)
        VALUES ('{name}', {activity_id})
        """
        )

    for s in ["Heim & Haus", "Arbeit", "Hobby"]:
        submit_sql(
            f"""
            INSERT INTO spaces (name)
            VALUES ('{s}')
            """
        )
