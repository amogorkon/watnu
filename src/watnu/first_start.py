
print("FIRST START")

def run(db, query, config, logger):
    statement = f"""
    CREATE TABLE IF NOT EXISTS spaces(
    space_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL UNIQUE,
    priority REAL DEFAULT 0
    )
    """

    if not query.exec_(statement):
        logger.warning("SQL failed:\n" + statement, query.lastError())

    statement = f"""
    CREATE TABLE IF NOT EXISTS activities(
    activity_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL UNIQUE
    )
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
    finished INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (task_id)
    REFERENCES tasks (id)
        ON DELETE CASCADE
    )
    """
    if not query.exec_(statement):
        logger.warning("SQL failed:\n" + statement, query.lastError())


    statement = f"""
    CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    do VARCHAR(280) NOT NULL,

    notes TEXT,
    url VARCHAR(280),
    attachments BLOB,
    space_id INTEGER,

    done INTEGER NOT NULL DEFAULT 0,
    draft INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1,
    deleted INTEGER NOT NULL DEFAULT 0,

    priority REAL NOT NULL DEFAULT 0,
    level_id INTEGER NOT NULL DEFAULT 0,

    deadline REAL NOT NULL DEFAULT "Infinity",
    workload INTEGER,

    activity_id INTEGER,
    difficulty REAL DEFAULT 5,
    fear REAL DEFAULT 5,
    embarassment REAL DEFAULT 5,

    last_checked INTEGER DEFAULT 0,
    chain TEXT,

    time_spent INTEGER DEFAULT 0,

    FOREIGN KEY (space_id)
    REFERENCES spaces (space_id)
        ON DELETE SET NULL,

    FOREIGN KEY (level_id)
    REFERENCES spaces (level_id)
        ON DELETE SET NULL,

    FOREIGN KEY (activity_id)
    REFERENCES activities (activity_id)
        ON DELETE SET NULL
    )
    """
    if not query.exec_(statement):
        logger.warning("SQL failed:\n" + statement)

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
