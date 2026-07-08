"""Persistence layer for survey responses.

On Posit Connect this app uses the per-content database: Connect provisions a
database for this content item and exposes its connection URL to the running
process through an environment variable. We look for the URL in a few
well-known variables (override the list with SCDS_DATABASE_URL_VARS, a
comma-separated list, if your Connect version uses a different name) and fall
back to a local SQLite file for development.

The connection URL is used through SQLAlchemy, so both Postgres and SQLite
per-content databases work unmodified.
"""

from __future__ import annotations

import datetime
import os
import uuid

import sqlalchemy as sa

DEFAULT_URL_VARS = (
    "CONNECT_CONTENT_DATABASE_URL",
    "POSIT_CONTENT_DATABASE_URL",
    "CONTENT_DATABASE_URL",
    "DATABASE_URL",
)

_LOCAL_SQLITE = "sqlite:///scds_responses.sqlite3"

metadata = sa.MetaData()

responses = sa.Table(
    "scds_responses",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("submission_id", sa.String(36), nullable=False, index=True),
    sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("question_number", sa.Integer, nullable=False),
    sa.Column("category", sa.String(32), nullable=False),
    sa.Column("points", sa.Integer, nullable=False),
)

_engine: sa.Engine | None = None


def _database_url() -> str:
    var_list = os.environ.get("SCDS_DATABASE_URL_VARS")
    candidates = (
        tuple(v.strip() for v in var_list.split(",") if v.strip())
        if var_list
        else DEFAULT_URL_VARS
    )
    for var in candidates:
        url = os.environ.get(var)
        if url:
            return _normalize_url(url)
    return _LOCAL_SQLITE


def _normalize_url(url: str) -> str:
    # Connect-provisioned Postgres URLs may use the postgres:// scheme, which
    # SQLAlchemy no longer accepts; route Postgres through the psycopg driver.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


def get_engine() -> sa.Engine:
    global _engine
    if _engine is None:
        _engine = sa.create_engine(_database_url(), pool_pre_ping=True)
        metadata.create_all(_engine)
    return _engine


def save_submission(points_by_question: list[dict[str, int]]) -> str:
    """Store one respondent's answers; returns the submission id.

    `points_by_question` holds one dict per question, mapping category name
    to the points assigned to that category's statement.
    """
    submission_id = str(uuid.uuid4())
    now = datetime.datetime.now(datetime.timezone.utc)
    rows = [
        {
            "submission_id": submission_id,
            "submitted_at": now,
            "question_number": qnum,
            "category": category,
            "points": pts,
        }
        for qnum, allocation in enumerate(points_by_question, start=1)
        for category, pts in allocation.items()
    ]
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(responses.insert(), rows)
    return submission_id


def respondent_count(exclude_submission: str | None = None) -> int:
    stmt = sa.select(
        sa.func.count(sa.distinct(responses.c.submission_id))
    )
    if exclude_submission is not None:
        stmt = stmt.where(responses.c.submission_id != exclude_submission)
    with get_engine().connect() as conn:
        return conn.execute(stmt).scalar_one()


def average_category_totals(
    exclude_submission: str | None = None,
) -> dict[str, float]:
    """Mean per-respondent total points in each category across submissions."""
    per_submission = (
        sa.select(
            responses.c.submission_id,
            responses.c.category,
            sa.func.sum(responses.c.points).label("total"),
        )
        .group_by(responses.c.submission_id, responses.c.category)
    )
    if exclude_submission is not None:
        per_submission = per_submission.where(
            responses.c.submission_id != exclude_submission
        )
    per_submission = per_submission.subquery()
    stmt = sa.select(
        per_submission.c.category,
        sa.func.avg(per_submission.c.total),
    ).group_by(per_submission.c.category)
    with get_engine().connect() as conn:
        return {row[0]: float(row[1]) for row in conn.execute(stmt)}


def category_totals(submission_id: str) -> dict[str, int]:
    stmt = (
        sa.select(
            responses.c.category,
            sa.func.sum(responses.c.points),
        )
        .where(responses.c.submission_id == submission_id)
        .group_by(responses.c.category)
    )
    with get_engine().connect() as conn:
        return {row[0]: int(row[1]) for row in conn.execute(stmt)}
