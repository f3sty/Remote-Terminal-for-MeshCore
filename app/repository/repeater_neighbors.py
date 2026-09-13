from app.database import db


class RepeaterNeighborRepository:
    @staticmethod
    async def merge_and_get(
        public_key: str,
        neighbors: list[dict],
        observed_at: int,
        boot_time: int | None = None,
    ) -> list[dict]:
        """Merge a fetch and return the accumulated neighbor list.

        ``last_heard_at`` is absolute so entries remain meaningful between fetches.
        """
        async with db.tx() as conn:
            for neighbor in neighbors:
                prefix = str(neighbor.get("pubkey", ""))
                if not prefix:
                    continue
                secs_ago = max(0, int(neighbor.get("secs_ago", 0)))
                await conn.execute(
                    """
                    INSERT INTO repeater_neighbors
                        (public_key, neighbor_prefix, snr, last_heard_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(public_key, neighbor_prefix) DO UPDATE SET
                        snr = excluded.snr,
                        last_heard_at = excluded.last_heard_at,
                        updated_at = excluded.updated_at
                    """,
                    (
                        public_key,
                        prefix,
                        float(neighbor.get("snr", 0.0)),
                        observed_at - secs_ago,
                        observed_at,
                    ),
                )

            if boot_time is not None:
                await conn.execute(
                    "DELETE FROM repeater_neighbors WHERE public_key = ? AND last_heard_at < ?",
                    (public_key, boot_time),
                )

            async with conn.execute(
                """
                SELECT neighbor_prefix, snr, last_heard_at
                FROM repeater_neighbors
                WHERE public_key = ?
                ORDER BY last_heard_at DESC, neighbor_prefix
                """,
                (public_key,),
            ) as cursor:
                rows = await cursor.fetchall()

        return [
            {
                "pubkey": row["neighbor_prefix"],
                "snr": row["snr"],
                "last_heard_at": row["last_heard_at"],
            }
            for row in rows
        ]

    @staticmethod
    async def get(public_key: str, observed_at: int, boot_time: int | None = None) -> list[dict]:
        """Return stored neighbors, pruning entries from before the last boot."""
        async with db.tx() as conn:
            if boot_time is not None:
                await conn.execute(
                    "DELETE FROM repeater_neighbors WHERE public_key = ? AND last_heard_at < ?",
                    (public_key, boot_time),
                )
            async with conn.execute(
                """
                SELECT neighbor_prefix, snr, last_heard_at
                FROM repeater_neighbors
                WHERE public_key = ?
                ORDER BY last_heard_at DESC, neighbor_prefix
                """,
                (public_key,),
            ) as cursor:
                rows = await cursor.fetchall()
        return [
            {
                "pubkey": row["neighbor_prefix"],
                "snr": row["snr"],
                "last_heard_at": row["last_heard_at"],
            }
            for row in rows
        ]

    @staticmethod
    async def clear(public_key: str) -> None:
        async with db.tx() as conn:
            await conn.execute("DELETE FROM repeater_neighbors WHERE public_key = ?", (public_key,))
