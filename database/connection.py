"""
Database connection module for Azure PostgreSQL
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Connection string for Azure PostgreSQL - changed from asyncpg to psycopg2
CONNECTION_STRING = "postgresql+psycopg2://postgres:748zt7gPN1VhKGr@trendo6rupgs.postgres.database.azure.com/trendo"

# Create sync engine
engine = create_engine(
    CONNECTION_STRING,
    echo=True,  # Set to False in production
)

# Create sync session maker
Session = sessionmaker(
    engine,
    expire_on_commit=False
)

# Base class for ORM models
Base = declarative_base()

# Example model - customize according to your database schema
class ExampleModel(Base):
    __tablename__ = "example_table"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)

# Function to get a database session
def get_db():
    """
    Get a database session for synchronous context
    Usage:
        with get_db() as session:
            result = session.execute(...)
    """
    session = Session()
    try:
        yield session
    finally:
        session.close()

# Example function to test the database connection
def test_connection():
    """Test the database connection by executing a simple query"""
    try:
        session = Session()
        # Execute a simple test query
        result = session.execute(text("SELECT 1"))
        print("Database connection successful!")
        print(f"Query result: {result.scalar()}")
        session.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return False

# Example function to query data
def fetch_example_data():
    """Fetch example data from the database"""
    session = Session()
    result = session.execute(text("SELECT current_database(), current_user"))
    db_info = result.first()
    session.close()
    return {
        "database": db_info[0],
        "user": db_info[1]
    }

def fetch_news_articles_schema():
    """
    Fetch the schema information for the public.news_articles table
    
    Returns:
        list: A list of dictionaries containing column information
    """
    session = Session()
    try:
        # SQL query to get table schema information
        query = text("""
            SELECT 
                column_name, 
                data_type, 
                character_maximum_length,
                column_default,
                is_nullable
            FROM 
                information_schema.columns
            WHERE 
                table_schema = 'public' AND 
                table_name = 'news_articles'
            ORDER BY 
                ordinal_position
        """)
        
        result = session.execute(query)
        columns = []
        
        for row in result:
            columns.append({
                "column_name": row[0],
                "data_type": row[1],
                "max_length": row[2],
                "default_value": row[3],
                "is_nullable": row[4]
            })
        
        print(columns)
        return columns
    except Exception as e:
        print(f"Error fetching schema: {str(e)}")
        return []
    finally:
        session.close()

# Run connection test if this file is executed directly
if __name__ == "__main__":
    test_connection()