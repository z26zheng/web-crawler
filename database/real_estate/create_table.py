"""
Module for creating and managing the real_estate table in the database
"""
import os
import sys

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

# Import from the new database module location
from database import Session, engine
from sqlalchemy import text

def drop_real_estate_tables():
    """
    Drop the real_estate_images and real_estate tables if they exist
    
    Note: We drop real_estate_images first because it has a foreign key reference to real_estate
    
    Returns:
        bool: True if tables were dropped successfully, False otherwise
    """
    session = Session()
    try:
        # Drop real_estate_images table first due to foreign key constraint
        query_drop_images = text("""
        DROP TABLE IF EXISTS public.real_estate_images;
        """)
        
        # Then drop the real_estate table
        query_drop_real_estate = text("""
        DROP TABLE IF EXISTS public.real_estate;
        """)
        
        session.execute(query_drop_images)
        session.execute(query_drop_real_estate)
        session.commit()
        print("Successfully dropped real_estate tables")
        return True
    except Exception as e:
        print(f"Error dropping real_estate tables: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

def create_real_estate_table():
    """
    Create the public.real_estate table if it doesn't exist
    
    Fields:
    - source_url: JSONB - stores source URL information
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
        # SQL query to create the real_estate table
        query = text("""
        CREATE TABLE IF NOT EXISTS public.real_estate (
            id SERIAL PRIMARY KEY,
            source_url JSONB,
            address JSONB NOT NULL,
            pending_date DATE,
            status VARCHAR(50),
            price INTEGER,
            qr_code_url TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create index on address for faster lookups using JSONB operators
        CREATE INDEX IF NOT EXISTS idx_real_estate_address ON public.real_estate USING GIN (address);
        
        -- Create index on status for filtering
        CREATE INDEX IF NOT EXISTS idx_real_estate_status ON public.real_estate(status);
        
        -- Create index on price for range queries
        CREATE INDEX IF NOT EXISTS idx_real_estate_price ON public.real_estate(price);
        """)
        
        session.execute(query)
        session.commit()
        print("Successfully created public.real_estate table")
        return True
    except Exception as e:
        print(f"Error creating real_estate table: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

def create_real_estate_images_table():
    """
    Create the public.real_estate_images table if it doesn't exist
    
    Fields:
    - real_estate_id: INTEGER - foreign key reference to the real_estate table
    - source_image_url: TEXT - stores a URL for the original image
    - generated_image_url: TEXT - stores a URL for the generated image
    - stats: TEXT - stores statistics or information about the image
    
    Returns:
        bool: True if the table was created successfully, False otherwise
    """
    session = Session()
    try:
        # SQL query to create the real_estate_images table
        query = text("""
        CREATE TABLE IF NOT EXISTS public.real_estate_images (
            id SERIAL PRIMARY KEY,
            real_estate_id INTEGER NOT NULL,
            source_image_url TEXT,
            generated_image_url TEXT,
            stats TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (real_estate_id) REFERENCES public.real_estate (id) ON DELETE CASCADE
        );
        
        -- Create index on real_estate_id for faster lookups and joins
        CREATE INDEX IF NOT EXISTS idx_real_estate_images_real_estate_id ON public.real_estate_images(real_estate_id);
        """)
        
        session.execute(query)
        session.commit()
        print("Successfully created public.real_estate_images table")
        return True
    except Exception as e:
        print(f"Error creating real_estate_images table: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

# Allow this module to be run as a script
if __name__ == "__main__":
    # First drop the existing tables
    drop_real_estate_tables()
    
    # Then create the new tables
    create_real_estate_table()
    create_real_estate_images_table()