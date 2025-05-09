"""adding default settings and new settings for search

Revision ID: 51be5ea962eb
Revises: 4465a755ecb6
Create Date: 2025-04-30 12:02:38.336214

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51be5ea962eb'
down_revision: Union[str, None] = '4465a755ecb6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('user_settings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('default_lowest_price', sa.Integer(), nullable=True),
        sa.Column('default_highest_price', sa.Integer(), nullable=True),
        sa.Column('default_location_id', sa.String(), nullable=True),
        sa.Column('default_location_name', sa.String(), nullable=True),
        sa.Column('default_location_radius_km', sa.Integer(), nullable=True),
        sa.Column('default_ad_type', sa.Enum('OFFERED', 'WANTED', 'OTHER', name='default_item_ad_type', native_enum=False), nullable=True),
        sa.Column('default_poster_type', sa.Enum('COMMERCIAL', 'PRIVATE', 'OTHER', name='default_item_poster_type', native_enum=False), nullable=True),
        sa.Column('default_is_picture_required', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_settings_user_id'), 'user_settings', ['user_id'], unique=False)

    op.add_column('search_settings', sa.Column('alias', sa.String(), nullable=True))
    op.add_column('search_settings', sa.Column('lowest_price', sa.Integer(), nullable=True))
    op.add_column('search_settings', sa.Column('highest_price', sa.Integer(), nullable=True))
    op.add_column('search_settings', sa.Column('category_id', sa.String(), nullable=True))
    op.add_column('search_settings', sa.Column('category_name', sa.String(), nullable=True))
    op.add_column('search_settings', sa.Column('ad_type', sa.Enum('OFFERED', 'WANTED', 'OTHER', name='item_ad_type', native_enum=False), nullable=True))
    op.add_column('search_settings', sa.Column('poster_type', sa.Enum('COMMERCIAL', 'PRIVATE', 'OTHER', name='item_poster_type', native_enum=False), nullable=True))
    op.add_column('search_settings', sa.Column('is_picture_required', sa.Boolean(), nullable=True))

    bind = op.get_bind()
    bind.execute(sa.text("""
        UPDATE search_settings
        SET alias = item_name
        WHERE alias IS NULL
    """))

    import uuid
    from datetime import datetime
    users = bind.execute(sa.text("SELECT user_id FROM users")).fetchall()
    now = datetime.utcnow()

    for row in users:
        user_id = row[0] if isinstance(row, tuple) else row.user_id
        bind.execute(sa.text("""
            INSERT INTO user_settings (
                id, user_id, created_at, updated_at,
                default_lowest_price, default_highest_price,
                default_location_radius_km, default_is_picture_required,
                default_ad_type, default_poster_type
            ) VALUES (
                :id, :user_id, :created_at, :updated_at,
                :default_lowest_price, :default_highest_price,
                :radius, :is_pic, :ad_type, :poster_type
            )
        """), {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "created_at": now,
            "updated_at": now,
            "default_lowest_price": 0,
            "default_highest_price": 10000,
            "radius": 10,
            "is_pic": False,
            "ad_type": 'OFFERED',
            "poster_type": 'PRIVATE'
        })



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('search_settings', 'is_picture_required')
    op.drop_column('search_settings', 'poster_type')
    op.drop_column('search_settings', 'ad_type')
    op.drop_column('search_settings', 'category_name')
    op.drop_column('search_settings', 'category_id')
    op.drop_column('search_settings', 'highest_price')
    op.drop_column('search_settings', 'lowest_price')
    op.drop_column('search_settings', 'alias')

    op.drop_index(op.f('ix_user_settings_user_id'), table_name='user_settings')
    op.drop_table('user_settings')

    op.execute("DROP TYPE IF EXISTS default_item_ad_type")
    op.execute("DROP TYPE IF EXISTS default_item_poster_type")
    op.execute("DROP TYPE IF EXISTS item_ad_type")
    op.execute("DROP TYPE IF EXISTS item_poster_type")