"""
RealEstate models using SQLAlchemy ORM for database operations
"""
from datetime import date, datetime
from typing import Dict, List, Optional, Any

import json
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, func, JSON
from sqlalchemy.orm import relationship

from database import Base

class RealEstate(Base):
    """
    SQLAlchemy ORM model for real_estate table
    
    Fields match the database schema defined in create_table.py:
    - id: Auto-incrementing primary key
    - source_url: JSON data storing source URL information
    - address: The property address (required)
    - pending_date: Date when the property is pending
    - status: Current status of the property
    - qr_code_url: URL for QR code associated with property
    - created_at: Timestamp when record was created
    - updated_at: Timestamp when record was last updated
    """
    __tablename__ = "real_estate"

    # Columns
    id = Column(Integer, primary_key=True)
    source_url = Column(JSON, default={})
    address = Column(Text, nullable=False)
    pending_date = Column(Date)
    status = Column(String(50))
    qr_code_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    images = relationship("RealEstateImage", back_populates="real_estate", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'address': self.address,
            'source_url': self.source_url,
            'pending_date': self.pending_date,
            'status': self.status,
            'qr_code_url': self.qr_code_url,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RealEstate':
        """Create model from dictionary"""
        data_copy = data.copy()
        
        # Convert JSON fields if they're strings
        if 'source_url' in data_copy and isinstance(data_copy['source_url'], str):
            data_copy['source_url'] = json.loads(data_copy['source_url'])
        
        return cls(**data_copy)


class RealEstateImage(Base):
    """
    SQLAlchemy ORM model for real_estate_images table
    
    Fields:
    - id: Auto-incrementing primary key
    - real_estate_id: Foreign key reference to the real_estate table
    - source_image_url: URL for the original image
    - generated_image_url: URL for the generated image
    - stats: Statistics or information about the image
    - created_at: Timestamp when record was created
    - updated_at: Timestamp when record was last updated
    """
    __tablename__ = "real_estate_images"
    
    # Columns
    id = Column(Integer, primary_key=True)
    real_estate_id = Column(Integer, ForeignKey('real_estate.id', ondelete='CASCADE'), nullable=False)
    source_image_url = Column(Text)
    generated_image_url = Column(Text)
    stats = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    real_estate = relationship("RealEstate", back_populates="images")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'real_estate_id': self.real_estate_id,
            'source_image_url': self.source_image_url,
            'generated_image_url': self.generated_image_url,
            'stats': self.stats,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RealEstateImage':
        """Create model from dictionary"""
        return cls(**data.copy())