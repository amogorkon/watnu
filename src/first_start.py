import sqlite3
from pathlib import Path

print("FIRST START")

schema = Path("schema.sql").read_text()

def setUp(db: sqlite3.Connection) -> None:
    db.executescript(schema)

    ### Default Entries ### 
    # TODO: internationalize

    for name, level_id in zip(
        ["MUST NOT", "SHOULD NOT", "COULD", "SHOULD", "MUST"],
        [-2, -1, 0, 1, 2],
    ):
        db.execute(
            f"""
        INSERT INTO levels (name, level_id)
        VALUES ('{name}', {level_id})
        """
        )

    for s in ["Heim & Haus", "Arbeit", "Hobby"]:
        db.execute(
            f"""
            INSERT INTO spaces (name)
            VALUES ('{s}')
            """
        )
    db.commit()
