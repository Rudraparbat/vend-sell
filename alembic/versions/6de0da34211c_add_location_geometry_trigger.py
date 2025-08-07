"""add_location_geometry_trigger

Revision ID: 6de0da34211c
Revises: d30f6ef88d31
Create Date: 2025-08-07 14:35:32.834225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6de0da34211c'
down_revision: Union[str, Sequence[str], None] = 'd30f6ef88d31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add trigger function and trigger for auto-updating geometry"""
    
    # Create the trigger function
    op.execute('''
        CREATE OR REPLACE FUNCTION update_location_geometry()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.location = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    ''')
    
    # Create the trigger
    op.execute('''
        CREATE TRIGGER trigger_update_location_geometry
            BEFORE INSERT OR UPDATE ON locations
            FOR EACH ROW
            EXECUTE FUNCTION update_location_geometry();
    ''')
    
    # Update existing records with geometry
    op.execute('''
        UPDATE locations 
        SET location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL AND location IS NULL;
    ''')

def downgrade() -> None:
    """Remove trigger and function"""
    
    # Drop trigger
    op.execute('DROP TRIGGER IF EXISTS trigger_update_location_geometry ON locations;')
    
    # Drop function
    op.execute('DROP FUNCTION IF EXISTS update_location_geometry();')
