"""geloactaion_migrate

Revision ID: d30f6ef88d31
Revises: 
Create Date: 2025-08-07 13:49:11.161617

"""
from typing import Sequence, Union
from alembic import op
import geoalchemy2
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd30f6ef88d31'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # Enable PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis;')
    
    # Add geometry column with IF NOT EXISTS protection
    try:
        op.add_column('locations', sa.Column(
            'location', 
            geoalchemy2.types.Geometry(
                geometry_type='POINT', 
                srid=4326, 
                dimension=2, 
                from_text='ST_GeomFromEWKT', 
                name='geometry'
            ), 
            nullable=True
        ))
    except Exception as e:
        print(f"Column might already exist: {e}")
    
    # Create spatial index with protection
    op.execute('''
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE tablename = 'locations' 
                AND indexname = 'idx_locations_location'
            ) THEN
                CREATE INDEX idx_locations_location 
                ON locations USING GIST (location);
            END IF;
        END $$;
    ''')

def downgrade() -> None:
    """Downgrade schema."""
    # Drop index if exists
    op.execute('DROP INDEX IF EXISTS idx_locations_location;')
    
    # Drop column if exists
    try:
        op.drop_column('locations', 'location')
    except Exception as e:
        print(f"Column might not exist: {e}")
