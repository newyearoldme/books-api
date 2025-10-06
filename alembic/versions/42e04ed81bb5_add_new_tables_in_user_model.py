"""add new tables in user model

Revision ID: 42e04ed81bb5
Revises: 4c0750c1853b
Create Date: 2025-10-05 14:00:25.174400

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "42e04ed81bb5"
down_revision: Union[str, Sequence[str], None] = "4c0750c1853b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
