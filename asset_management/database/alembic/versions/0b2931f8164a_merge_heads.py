"""merge heads

Revision ID: 0b2931f8164a
Revises: 8b2c1c3d4e5f, 9e1ff39517d0
Create Date: 2026-01-11 12:15:55.733414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b2931f8164a'
down_revision: Union[str, Sequence[str], None] = ('8b2c1c3d4e5f', '9e1ff39517d0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
