"""entity-collection_id

Revision ID: e57bb1034c2c
Revises: 70f218fa236f
Create Date: 2022-12-16 01:53:03.130621

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e57bb1034c2c'
down_revision = '70f218fa236f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('entity', sa.Column('collection_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'entity', 'collection', ['collection_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'entity', type_='foreignkey')
    op.drop_column('entity', 'collection_id')
    # ### end Alembic commands ###