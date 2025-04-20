"""
Module for creating and managing the property_metadata table in the database
"""
import os
import sys

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

# Import from the new database module location
from database import Session, engine
from sqlalchemy import text

def drop_property_tables():
    """
    Drop the property_images and property_metadata tables if they exist
    
    Note: We drop property_images first because it has a foreign key reference to property_metadata
    
    Returns:
        bool: True if tables were dropped successfully, False otherwise
    """
    session = Session()
    try:
        # Drop property_images table first due to foreign key constraint
        query_drop_images = text("""
        DROP TABLE IF EXISTS public.property_images;
        """)
        
        # Then drop the property_metadata table
        query_drop_property_metadata = text("""
        DROP TABLE IF EXISTS public.property_metadata;
        """)
        
        session.execute(query_drop_images)
        session.execute(query_drop_property_metadata)
        session.commit()
        print("Successfully dropped property_metadata tables")
        return True
    except Exception as e:
        print(f"Error dropping property_metadata tables: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

def create_property_metadata_table():
    """
    Create the public.property_metadata table if it doesn't exist
    
    Fields:
    - source_url: TEXT - stores source URL as a string (unique constraint)
    - address: JSONB - stores address information
    - pending_date: DATE - stores a date
    - status: VARCHAR(50) - stores a string representing status
    - price: INTEGER - stores the property price
    - qr_code_url: TEXT - stores a URL for QR code
    
    Returns:
        bool: True if the table was created successfully, False otherwise
    """
    session = Session()
    try:
        # SQL query to create the property_metadata table
        query = text("""
        CREATE TABLE IF NOT EXISTS public.property_metadata (
            id SERIAL PRIMARY KEY,
            source_url TEXT UNIQUE,
            address JSONB NOT NULL,
            pending_date DATE,
            status VARCHAR(50),
            price INTEGER,
            qr_code_url TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create index on address for faster lookups using JSONB operators
        CREATE INDEX IF NOT EXISTS idx_property_metadata_address ON public.property_metadata USING GIN (address);
        
        -- Create index on status for filtering
        CREATE INDEX IF NOT EXISTS idx_property_metadata_status ON public.property_metadata(status);
        
        -- Create index on price for range queries
        CREATE INDEX IF NOT EXISTS idx_property_metadata_price ON public.property_metadata(price);
        
        -- Create index on source_url for uniqueness checks
        CREATE INDEX IF NOT EXISTS idx_property_metadata_source_url ON public.property_metadata(source_url);
        """)
        
        session.execute(query)
        session.commit()
        print("Successfully created public.property_metadata table")
        return True
    except Exception as e:
        print(f"Error creating property_metadata table: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

def create_property_images_table():
    """
    Create the public.property_images table if it doesn't exist
    
    Fields:
    - property_metadata_id: INTEGER - foreign key reference to the property_metadata table
    - category: VARCHAR(50) - stores the image category (e.g. Kitchen, Bathroom)
    - source_image_url: TEXT - stores a URL for the original image (unique constraint)
    - generated_image_url: TEXT - stores a URL for the generated image
    - state: TEXT - stores the state information about the image
    
    Returns:
        bool: True if the table was created successfully, False otherwise
    """
    session = Session()
    try:
        # SQL query to create the property_images table
        query = text("""
        CREATE TABLE IF NOT EXISTS public.property_images (
            id SERIAL PRIMARY KEY,
            property_metadata_id INTEGER NOT NULL,
            category VARCHAR(50),
            source_image_url TEXT UNIQUE,
            generated_image_url TEXT,
            state TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (property_metadata_id) REFERENCES public.property_metadata (id) ON DELETE CASCADE
        );
        
        -- Create index on property_metadata_id for faster lookups and joins
        CREATE INDEX IF NOT EXISTS idx_property_images_property_metadata_id ON public.property_images(property_metadata_id);
        
        -- Create index on category for filtering
        CREATE INDEX IF NOT EXISTS idx_property_images_category ON public.property_images(category);
        
        -- Create index on source_image_url for uniqueness checks
        CREATE INDEX IF NOT EXISTS idx_property_images_source_url ON public.property_images(source_image_url);
        """)
        
        session.execute(query)
        session.commit()
        print("Successfully created public.property_images table")
        return True
    except Exception as e:
        print(f"Error creating property_images table: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

# Allow this module to be run as a script
if __name__ == "__main__":
    # First drop the existing tables
    drop_property_tables()
    
    # Then create the new tables
    create_property_metadata_table()
    create_property_images_table()