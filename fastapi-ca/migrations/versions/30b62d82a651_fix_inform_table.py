"""fix Inform Table

Revision ID: 30b62d82a651
Revises: e115f42fbb6c
Create Date: 2025-02-09 22:03:24.398043

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '30b62d82a651'
down_revision: Union[str, None] = 'e115f42fbb6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Inform',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('dataset_id', sa.String(length=36), nullable=False),
    sa.Column('model_config_path', sa.Text(), nullable=False),
    sa.Column('user_config_path', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('Config')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Config',
    sa.Column('id', mysql.VARCHAR(length=36), nullable=False),
    sa.Column('dataset_id', mysql.VARCHAR(length=36), nullable=False),
    sa.Column('path', mysql.TEXT(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('Inform')
    # ### end Alembic commands ###
