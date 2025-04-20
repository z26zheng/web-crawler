"""
PropertyMetadata models using SQLAlchemy ORM for database operations
"""
from datetime import date, datetime
from typing import Dict, List, Optional, Any

import json
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, func, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from database import Base

class PropertyMetadata(Base):
    """
    SQLAlchemy ORM model for property_metadata table
    
    Fields match the database schema defined in create_table.py:
    - id: Auto-incrementing primary key
    - source_url: String storing the property source URL (unique)
    - address: JSONB data storing address information (required)
    - pending_date: Date when the property is pending
    - status: Current status of the property
    - price: Integer for the property price
    - qr_code_url: URL for QR code associated with property
    - created_at: Timestamp when record was created
    - updated_at: Timestamp when record was last updated
    """
    __tablename__ = "property_metadata"

    # Columns
    id = Column(Integer, primary_key=True)
    source_url = Column(Text, unique=True)
    address = Column(JSONB, nullable=False)
    pending_date = Column(Date)
    status = Column(String(50))
    price = Column(Integer)
    qr_code_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'address': self.address,
            'source_url': self.source_url,
            'pending_date': self.pending_date,
            'status': self.status,
            'price': self.price,
            'qr_code_url': self.qr_code_url,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PropertyMetadata':
        """Create model from dictionary"""
        data_copy = data.copy()
        
        # Convert address field if it's a string
        if 'address' in data_copy and isinstance(data_copy['address'], str):
            data_copy['address'] = json.loads(data_copy['address'])
        
        return cls(**data_copy)


class PropertyImage(Base):
    """
    SQLAlchemy ORM model for property_images table
    
    Fields:
    - id: Auto-incrementing primary key
    - property_id: Foreign key reference to the property_metadata table
    - source_image_url: URL for the original image
    - generated_image_url: URL for the generated image
    - stats: Statistics or information about the image
    - created_at: Timestamp when record was created
    - updated_at: Timestamp when record was last updated
    """
    __tablename__ = "property_images"
    
    # Columns
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('property_metadata.id', ondelete='CASCADE'), nullable=False)
    source_image_url = Column(Text)
    generated_image_url = Column(Text)
    stats = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    property = relationship("PropertyMetadata", back_populates="images")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'property_id': self.property_id,
            'source_image_url': self.source_image_url,
            'generated_image_url': self.generated_image_url,
            'stats': self.stats,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PropertyImage':
        """Create model from dictionary"""
        return cls(**data.copy())