"""
Database package initialization
"""
# Import everything from the connection module to maintain the same API
from database.connection import (
    engine,
    Session,
    Base,
    ExampleModel,
    get_db,
    test_connection,
    fetch_example_data,
    fetch_news_articles_schema
)

# This allows importing directly from the database package
# e.g., from database import Session, engine
__all__ = [
    'engine',
    'Session',
    'Base',
    'ExampleModel',
    'get_db',
    'test_connection',
    'fetch_example_data',
    'fetch_news_articles_schema'
]