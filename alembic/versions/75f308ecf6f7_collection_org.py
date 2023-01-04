"""collection-org

Revision ID: 75f308ecf6f7
Revises: 9ede3e883ff8
Create Date: 2023-01-03 18:08:09.442732

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75f308ecf6f7'
down_revision = '9ede3e883ff8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('collection', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'collection', 'organization', ['organization_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'collection', type_='foreignkey')
    op.drop_column('collection', 'organization_id')
    # ### end Alembic commands ###
