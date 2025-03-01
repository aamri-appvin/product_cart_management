# """adding new columns

# Revision ID: ef967a27d7a3
# Revises: f313b903ef3b
# Create Date: 2025-01-29 18:31:44.270477

# """
# from typing import Sequence, Union

# from alembic import op
# import sqlalchemy as sa


# # revision identifiers, used by Alembic.
# revision: str = 'ef967a27d7a3'
# down_revision: Union[str, None] = 'f313b903ef3b'
# branch_labels: Union[str, Sequence[str], None] = None
# depends_on: Union[str, Sequence[str], None] = None


# def upgrade() -> None:
#     # ### commands auto generated by Alembic - please adjust! ###
#     op.add_column('cart_items', sa.Column('created_at', sa.Time(), nullable=False))
#     op.add_column('cart_items', sa.Column('updated_at', sa.Time(), nullable=False))
#     op.add_column('deleted_products', sa.Column('created_at', sa.Time(), nullable=False))
#     op.add_column('deleted_products', sa.Column('updated_at', sa.Time(), nullable=False))
#     op.add_column('products', sa.Column('created_at', sa.Time(), nullable=False))
#     op.add_column('products', sa.Column('updated_at', sa.Time(), nullable=False))
#     # ### end Alembic commands ###


# def downgrade() -> None:
#     # ### commands auto generated by Alembic - please adjust! ###
#     op.drop_column('products', 'updated_at')
#     op.drop_column('products', 'created_at')
#     op.drop_column('deleted_products', 'updated_at')
#     op.drop_column('deleted_products', 'created_at')
#     op.drop_column('cart_items', 'updated_at')
#     op.drop_column('cart_items', 'created_at')
#     # ### end Alembic commands ###
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef967a27d7a3'
down_revision = 'f313b903ef3b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cart_items', sa.Column('created_at', sa.Time(), server_default=sa.text('now()'), nullable=False))
    op.add_column('cart_items', sa.Column('updated_at', sa.Time(), server_default=sa.text('now()'), nullable=False))
    op.add_column('deleted_products', sa.Column('created_at', sa.Time(), server_default=sa.text('now()'), nullable=False))
    op.add_column('deleted_products', sa.Column('updated_at', sa.Time(), server_default=sa.text('now()'), nullable=False))
    op.add_column('products', sa.Column('created_at', sa.Time(), server_default=sa.text('now()'), nullable=False))
    op.add_column('products', sa.Column('updated_at', sa.Time(), server_default=sa.text('now()'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'updated_at')
    op.drop_column('products', 'created_at')
    op.drop_column('deleted_products', 'updated_at')
    op.drop_column('deleted_products', 'created_at')
    op.drop_column('cart_items', 'updated_at')
    op.drop_column('cart_items', 'created_at')
    # ### end Alembic commands ###
