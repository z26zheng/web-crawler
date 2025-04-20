"""
Module for handling property metadata operations using SQLAlchemy ORM
"""
import os
import sys
from typing import List, Optional, Dict, Any

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from database import Session
from database.real_estate.models import PropertyMetadata, PropertyImage

# Property Metadata Operations

def add_property(address: Dict[str, Any], source_url: Dict[str, Any] = None, 
                pending_date: Optional[str] = None, status: Optional[str] = None, 
                price: Optional[int] = None, qr_code_url: Optional[str] = None) -> int:
    """
    Add a new property using SQLAlchemy ORM
    
    Args:
        address: Property address as a dictionary (required)
        source_url: Source URL information
        pending_date: Date when the property is pending
        status: Current status of the property
        price: Integer value representing property price
        qr_code_url: URL for QR code
        
    Returns:
        int: ID of the newly created property record
        
    Raises:
        Exception: If there was an error adding the property
    """
    session = Session()
    try:
        # Create a new PropertyMetadata instance
        new_property = PropertyMetadata(
            address=address,
            source_url=source_url or {},
            pending_date=pending_date,
            status=status,
            price=price,
            qr_code_url=qr_code_url
        )
        
        # Add to session and commit
        session.add(new_property)
        session.commit()
        
        # Return the new ID
        return new_property.id
    except Exception as e:
        session.rollback()
        raise Exception(f"Error adding property: {str(e)}")
    finally:
        session.close()

def get_property(property_id: int) -> Optional[PropertyMetadata]:
    """
    Get a property by ID using SQLAlchemy ORM
    
    Args:
        property_id: ID of the property to retrieve
        
    Returns:
        Optional[PropertyMetadata]: Property object if found, None otherwise
        
    Raises:
        Exception: If there was an error retrieving the property
    """
    session = Session()
    try:
        # Query using SQLAlchemy ORM
        property = session.query(PropertyMetadata).filter(PropertyMetadata.id == property_id).first()
        return property
    except Exception as e:
        raise Exception(f"Error retrieving property: {str(e)}")
    finally:
        session.close()

def get_properties(limit: int = 100, offset: int = 0) -> List[PropertyMetadata]:
    """
    Get a list of properties using SQLAlchemy ORM
    
    Args:
        limit: Maximum number of properties to retrieve
        offset: Number of properties to skip
        
    Returns:
        List[PropertyMetadata]: List of property objects
        
    Raises:
        Exception: If there was an error retrieving properties
    """
    session = Session()
    try:
        # Query using SQLAlchemy ORM with pagination
        properties = (
            session.query(PropertyMetadata)
            .order_by(PropertyMetadata.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return properties
    except Exception as e:
        raise Exception(f"Error retrieving properties: {str(e)}")
    finally:
        session.close()

def update_property(property_id: int, updates: Dict[str, Any]) -> bool:
    """
    Update an existing property using SQLAlchemy ORM
    
    Args:
        property_id: ID of the property to update
        updates: Dictionary of fields to update
        
    Returns:
        bool: True if update was successful
        
    Raises:
        Exception: If there was an error updating the property
    """
    session = Session()
    try:
        # Get the existing property
        property = session.query(PropertyMetadata).filter(PropertyMetadata.id == property_id).first()
        
        # If property doesn't exist, return False
        if not property:
            return False
        
        # Update only valid fields
        valid_fields = ["address", "source_url", "pending_date", "status", "price", "qr_code_url"]
        
        # Apply updates
        for key, value in updates.items():
            if key in valid_fields and hasattr(property, key):
                setattr(property, key, value)
        
        # Commit changes
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise Exception(f"Error updating property: {str(e)}")
    finally:
        session.close()

def delete_property(property_id: int) -> bool:
    """
    Delete a property using SQLAlchemy ORM
    
    Args:
        property_id: ID of the property to delete
        
    Returns:
        bool: True if deletion was successful
        
    Raises:
        Exception: If there was an error deleting the property
    """
    session = Session()
    try:
        # Get property by ID
        property = session.query(PropertyMetadata).filter(PropertyMetadata.id == property_id).first()
        
        # If property doesn't exist, return False
        if not property:
            return False
        
        # Delete the property (images will be deleted automatically due to cascade)
        session.delete(property)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise Exception(f"Error deleting property: {str(e)}")
    finally:
        session.close()

# Image Operations

def add_image(property_id: int, source_image_url: Optional[str] = None, 
              generated_image_url: Optional[str] = None, stats: Optional[str] = None) -> int:
    """
    Add a new image for a property using SQLAlchemy ORM
    
    Args:
        property_id: ID of the property
        source_image_url: URL of the source image
        generated_image_url: URL of the generated image
        stats: Statistics or information about the image
        
    Returns:
        int: ID of the newly created image record
    
    Raises:
        Exception: If there was an error adding the image
    """
    session = Session()
    try:
        # Create a new PropertyImage instance
        new_image = PropertyImage(
            property_id=property_id,
            source_image_url=source_image_url,
            generated_image_url=generated_image_url,
            stats=stats
        )
        
        # Add to session and commit
        session.add(new_image)
        session.commit()
        
        # Return the new ID
        return new_image.id
    except Exception as e:
        session.rollback()
        raise Exception(f"Error adding image: {str(e)}")
    finally:
        session.close()

def get_images_by_property_id(property_id: int) -> List[PropertyImage]:
    """
    Get all images for a specific property using SQLAlchemy ORM
    
    Args:
        property_id: ID of the property
        
    Returns:
        List[PropertyImage]: List of image records associated with the property
        
    Raises:
        Exception: If there was an error retrieving images
    """
    session = Session()
    try:
        # Query using SQLAlchemy ORM
        images = (
            session.query(PropertyImage)
            .filter(PropertyImage.property_id == property_id)
            .order_by(PropertyImage.created_at.desc())
            .all()
        )
        
        return images
    except Exception as e:
        raise Exception(f"Error retrieving images: {str(e)}")
    finally:
        session.close()

def update_image(image_id: int, updates: Dict[str, Any]) -> bool:
    """
    Update an existing property image using SQLAlchemy ORM
    
    Args:
        image_id: ID of the image to update
        updates: Dictionary of fields to update
        
    Returns:
        bool: True if update was successful
        
    Raises:
        Exception: If there was an error updating the image
    """
    session = Session()
    try:
        # Get the existing image
        image = session.query(PropertyImage).filter(PropertyImage.id == image_id).first()
        
        # If image doesn't exist, return False
        if not image:
            return False
        
        # Update only the fields that are provided in updates
        update_fields = {}
        for key, value in updates.items():
            if key in ["source_image_url", "generated_image_url", "stats"] and hasattr(image, key):
                update_fields[key] = value
        
        # Apply updates
        for key, value in update_fields.items():
            setattr(image, key, value)
        
        # Commit changes
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise Exception(f"Error updating image: {str(e)}")
    finally:
        session.close()

def delete_image(image_id: int) -> bool:
    """
    Delete a property image using SQLAlchemy ORM
    
    Args:
        image_id: ID of the image to delete
        
    Returns:
        bool: True if deletion was successful
        
    Raises:
        Exception: If there was an error deleting the image
    """
    session = Session()
    try:
        # Get image by ID
        image = session.query(PropertyImage).filter(PropertyImage.id == image_id).first()
        
        # If image doesn't exist, return False
        if not image:
            return False
        
        # Delete the image
        session.delete(image)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise Exception(f"Error deleting image: {str(e)}")
    finally:
        session.close()