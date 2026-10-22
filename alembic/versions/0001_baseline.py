"""baseline

Revision ID: 0001
Revises: 
Create Date: 2026-10-22 09:37:13.141173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
# Ergänzt: für den MySQL-Typ TINYINT.
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Ergänzt: Nur eine leere Datenbank braucht diese CREATE-Anweisungen.
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("first_name", sa.String(50), nullable=False),
        sa.Column("last_name", sa.String(50), nullable=False),
        sa.Column("house", sa.String(20), nullable=True),
        sa.Column("school_year", mysql.TINYINT(), nullable=False),
        sa.CheckConstraint(
            "school_year BETWEEN 1 AND 7",
            name="ck_students_school_year",
        ),
    )
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(100), nullable=False),
    )
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("booking_date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(
            ["student_id"], ["students.id"], name="fk_bookings_student"
        ),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"], name="fk_bookings_course"
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    raise RuntimeError("Die Baseline wird in diesem Kurs nicht entfernt.")
