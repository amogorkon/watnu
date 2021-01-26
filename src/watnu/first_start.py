
print("FIRST START")

def run(db, query, config, logger):

    ### CREATE SQL TABLES ###

    statement = f"""
CREATE TABLE "mantras" (
    "mantra_id" INTEGER NOT NULL UNIQUE,
    "text"  TEXT NOT NULL UNIQUE,
    "last_time" INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY("mantra_id" AUTOINCREMENT)
);
    """ 

    if not query.exec_(statement):
        logger.warning("SQL failed:\n" + statement, query.lastError())


    statement = f"""
CREATE TABLE "spaces" (
    "space_id"  INTEGER NOT NULL UNIQUE,
    "name"  VARCHAR(255) NOT NULL UNIQUE,
    "priority"  REAL DEFAULT 0,
    "primary_activity_id"   INTEGER,
    "secondary_activity_id" INTEGER,
    FOREIGN KEY("secondary_activity_id") REFERENCES "activities"("activity_id"),
    FOREIGN KEY("primary_activity_id") REFERENCES "activities"("activity_id"),
    PRIMARY KEY("space_id" AUTOINCREMENT)
)
    """

    if not query.exec_(statement):
        logger.warning("SQL failed:\n" + statement, query.lastError())

    statement = f"""
CREATE TABLE "skills" (
    "skill_id"   INTEGER NOT NULL UNIQUE,
    "name"  VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY("skill_id" AUTOINCREMENT)
);
    """
    if not query.exec_(statement):
        logger.warning("SQL failed:\n" + statement, query.lastError())


    statement = f"""
CREATE TABLE "activities" (
    "activity_id"   INTEGER NOT NULL UNIQUE,
    "name"  VARCHAR(255) NOT NULL UNIQUE,
    "adjust_time_spent" INTEGER DEFAULT 0,
    PRIMARY KEY("activity_id" AUTOINCREMENT)
);
    """
    if not query.exec_(statement):
        logger.warning("SQL failed:\n" + statement, query.lastError())

    statement = f"""
    CREATE TABLE IF NOT EXISTS levels(
    level_id INTEGER PRIMARY KEY UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL UNIQUE
    )
    """
    if not query.exec_(statement):
        logger.warning("SQL failed:\n" + statement, query.lastError())

    statement = f"""
    CREATE TABLE IF NOT EXISTS sessions(
    session_id INTEGER PRIMARY KEY UNIQUE NOT NULL,
    task_id INTEGER NOT NULL,
    start INTEGER NOT NULL,
    stop INTEGER NOT NULL,
    pause_time INTEGER NOT NULL DEFAULT 0,
    finished INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (task_id)
    REFERENCES tasks (id)
        ON DELETE CASCADE
    )
    """
    if not query.exec_(statement):
        logger.warning("SQL failed:\n" + statement, query.lastError())


    statement = f"""
CREATE TABLE "tasks" (
    "id"    INTEGER NOT NULL UNIQUE,
    "do"    VARCHAR(280) NOT NULL,
    "notes" TEXT,
    "url"   VARCHAR(280),
    "attachments"   BLOB,
    "space_id"  INTEGER,
    "done"  INTEGER NOT NULL DEFAULT 0,
    "draft" INTEGER NOT NULL DEFAULT 0,
    "inactive"    INTEGER NOT NULL DEFAULT 0,
    "deleted"   INTEGER NOT NULL DEFAULT 0,
    "habit"     INTEGER NOT NULL DEFAULT 0,
    "priority"  REAL NOT NULL DEFAULT 0,
    "level_id"  INTEGER NOT NULL DEFAULT 0,
    "deadline"  REAL NOT NULL DEFAULT Infinity,
    "workload"  INTEGER,
    "activity_id"   INTEGER,
    "secondary_activity_id"   INTEGER,
    "difficulty"    REAL DEFAULT 5,
    "fear"  REAL DEFAULT 5,
    "embarassment"  REAL DEFAULT 5,
    "last_checked"  INTEGER DEFAULT 0,
    "time_spent"    INTEGER DEFAULT 0,
    "adjust_time_spent" INTEGER DEFAULT 0,
    PRIMARY KEY("id" AUTOINCREMENT),
    FOREIGN KEY("level_id") REFERENCES "spaces"("level_id") ON DELETE SET NULL,
    FOREIGN KEY("activity_id") REFERENCES "activities"("activity_id") ON DELETE SET NULL,
    FOREIGN KEY("space_id") REFERENCES "spaces"("space_id") ON DELETE SET NULL
);
    """
    if not query.exec_(statement):
        logger.warning("SQL failed:\n" + statement)

    statement = f"""
CREATE TABLE "task_trains_skill" (
    "task_id"   INTEGER,
    "skill_id"  INTEGER,
    FOREIGN KEY("skill_id") REFERENCES "skills" ON DELETE CASCADE,
    FOREIGN KEY("task_id") REFERENCES "tasks" ON DELETE CASCADE
)
    """
    if not query.exec_(statement):
        logger.warning("SQL failed:\n" + statement, query.lastError())


    ### Default Entries ###

    for name, level_id in zip(
        ["MUST NOT", "SHOULD NOT", "COULD", "SHOULD", "MUST"],
        [-2,-1,0,1,2]):
        statement = f"""
        INSERT INTO levels (name, level_id)
        VALUES ('{name}', {level_id})
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)

    for name, activity_id in zip(
        ["BODY", "SPIRIT", "MIND"],
        [0,1,2]):
        statement = f"""
        INSERT INTO activities (name, activity_id)
        VALUES ('{name}', {activity_id})
        """
        if not query.exec_(statement):
            logger.warning("SQL failed:\n" + statement)

    statement = f"""
        INSERT INTO spaces (name, space_id, priority)
        VALUES ('foo', 0, 0)
        """
    if not query.exec_(statement):
        logger.warning("SQL failed:\n" + statement)
