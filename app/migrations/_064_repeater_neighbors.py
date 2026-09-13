import aiosqlite


async def migrate(conn: aiosqlite.Connection) -> None:
    """Persist accumulated repeater neighbor observations."""
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS repeater_neighbors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            public_key TEXT NOT NULL,
            neighbor_prefix TEXT NOT NULL,
            snr REAL NOT NULL,
            last_heard_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            UNIQUE(public_key, neighbor_prefix),
            FOREIGN KEY (public_key) REFERENCES contacts(public_key) ON DELETE CASCADE
        )
        """
    )
    await conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_repeater_neighbors_pk_heard
            ON repeater_neighbors(public_key, last_heard_at DESC)
        """
    )
    await conn.commit()
