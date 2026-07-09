import logging
from psycopg_pool import ConnectionPool
from psycopg import Error as PsycopgError

# from config import DATABASE_URL, POOL_MIN_SIZE, POOL_MAX_SIZE, POOL_TIMEOUT_SECONDS


# can move below in config.py
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/your_db",
)

POOL_MIN_SIZE = 1
POOL_MAX_SIZE = 3
POOL_TIMEOUT_SECONDS = 10  # max wait time to acquire a connection


logger = logging.getLogger(__name__)


def create_pool() -> ConnectionPool:
    """Creates the connection pool. Called once at app startup."""
    return ConnectionPool(
        conninfo=DATABASE_URL,
        min_size=POOL_MIN_SIZE,
        max_size=POOL_MAX_SIZE,
        timeout=POOL_TIMEOUT_SECONDS,
        open=True,
        kwargs={"autocommit": False},
    )


class PptSaveError(Exception):
    """Raised when saving a generated PPT to temp_template_store fails."""


def save_ppt_template(
    pool: ConnectionPool,
    pts_id: str,
    permit_type: str,
    ppt_bytes: bytes,
    file_name: str,
    created_by: str,
) -> dict:
    """
    Inserts a new versioned PPT record into temp_template_store.
    Increments version and flips is_latest within a single transaction.
    Raises PptSaveError on any DB failure.
    """
    try:
        with pool.connection() as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT COALESCE(MAX(version), 0) + 1
                        FROM temp_template_store
                        WHERE pts_id = %s AND permit_type = %s
                        """,
                        (pts_id, permit_type),
                    )
                    next_version = cur.fetchone()[0]

                    cur.execute(
                        """
                        UPDATE temp_template_store
                        SET is_latest = FALSE
                        WHERE pts_id = %s AND permit_type = %s AND is_latest = TRUE
                        """,
                        (pts_id, permit_type),
                    )

                    cur.execute(
                        """
                        INSERT INTO temp_template_store
                            (pts_id, permit_type, version, is_latest, ppt_blob,
                             file_name, file_size, created_by)
                        VALUES
                            (%s, %s, %s, TRUE, %s, %s, %s, %s)
                        RETURNING id, version, status, created_at
                        """,
                        (
                            pts_id,
                            permit_type,
                            next_version,
                            ppt_bytes,
                            file_name,
                            len(ppt_bytes),
                            created_by,
                        ),
                    )
                    row = cur.fetchone()

        return {
            "id": row[0],
            "version": row[1],
            "status": row[2],
            "created_at": row[3].isoformat(),
        }

    except PsycopgError:
        logger.exception(
            "Failed to save PPT template for pts_id=%s permit_type=%s",
            pts_id, permit_type,
        )
        raise PptSaveError(
            f"Could not save PPT template for pts_id={pts_id}, permit_type={permit_type}"
        )
