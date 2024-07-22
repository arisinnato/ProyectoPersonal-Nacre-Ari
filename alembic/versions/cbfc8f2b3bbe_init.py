"""init

Revision ID: cbfc8f2b3bbe
Revises: b597386c4dd2
Create Date: 2024-07-22 10:55:59.440278

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cbfc8f2b3bbe'
down_revision: Union[str, None] = 'b597386c4dd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('type', sa.String(), nullable=True))
    op.create_index(op.f('ix_items_type'), 'items', ['type'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_items_type'), table_name='items')
    op.drop_column('items', 'type')
    # ### end Alembic commands ###
