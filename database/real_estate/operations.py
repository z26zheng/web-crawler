"""
Module for handling property metadata operations using SQLAlchemy ORM
"""
import os
import sys
from typing import List, Optional, Dict, Any, Tuple

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from database import Session
from database.real_estate.models import PropertyMetadata, PropertyImage

# Property Metadata Operations

def add_property(property_metadata: PropertyMetadata) -> PropertyMetadata:
    """
    Add a new property using SQLAlchemy ORM
    
    Args:
        property_metadata: PropertyMetadata object to add to the database
        
    Returns:
        PropertyMetadata: Fresh PropertyMetadata object loaded from the database
        
    Raises:
        Exception: If there was an error adding the property
    """
    session = Session()
    try:
        # Add to session and commit
        session.add(property_metadata)
        session.commit()
        
        # Get the ID of the newly inserted property
        property_id = property_metadata.id
        
        # Refresh the property from the database to get the latest state
        fresh_property = session.query(PropertyMetadata).filter(
            PropertyMetadata.id == property_id
        ).first()
        
        return fresh_property
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

def upsert_property(property_metadata: PropertyMetadata) -> Tuple[PropertyMetadata, bool]:
    """
    Upsert (update or insert) a property based on source_url as the unique key
    
    Args:
        property_metadata: PropertyMetadata object to upsert
        
    Returns:
        Tuple[PropertyMetadata, bool]: (fresh_property, is_new) where:
            - fresh_property is a fresh PropertyMetadata object loaded from the database
            - is_new is True if a new record was created, False if an existing one was updated
        
    Raises:
        Exception: If there was an error upserting the property
    """
    if not property_metadata.source_url:
        raise ValueError("source_url is required for upsert operation")
    
    session = Session()
    try:
        # Check if a property with the given source_url already exists
        existing_property = session.query(PropertyMetadata).filter(
            PropertyMetadata.source_url == property_metadata.source_url
        ).first()
        
        is_new = False
        
        if existing_property:
            # Update the existing property with non-None values from the input
            if property_metadata.address is not None:
                existing_property.address = property_metadata.address
            if property_metadata.pending_date is not None:
                existing_property.pending_date = property_metadata.pending_date
            if property_metadata.status is not None:
                existing_property.status = property_metadata.status
            if property_metadata.price is not None:
                existing_property.price = property_metadata.price
            if property_metadata.qr_code_url is not None:
                existing_property.qr_code_url = property_metadata.qr_code_url
            
            property_id = existing_property.id
            
        else:
            # Create a new property
            session.add(property_metadata)
            is_new = True
        
        # Commit changes
        session.commit()
        
        # Get the ID based on whether it's new or existing
        property_id = property_metadata.id if is_new else existing_property.id
        
        # Refresh from database
        fresh_property = session.query(PropertyMetadata).filter(
            PropertyMetadata.id == property_id
        ).first()
        
        return fresh_property, is_new
    
    except Exception as e:
        session.rollback()
        raise Exception(f"Error upserting property: {str(e)}")
    finally:
        session.close()

# Image Operations

def add_image(property_image: PropertyImage) -> PropertyImage:
    """
    Add a new image for a property using SQLAlchemy ORM
    
    Args:
        property_image: PropertyImage object to add to the database
        
    Returns:
        PropertyImage: Fresh PropertyImage object loaded from the database
    
    Raises:
        Exception: If there was an error adding the image
    """
    session = Session()
    try:
        # Add to session and commit
        session.add(property_image)
        session.commit()
        
        # Get the ID of the newly inserted image
        image_id = property_image.id
        
        # Refresh the image from the database to get the latest state
        fresh_image = session.query(PropertyImage).filter(
            PropertyImage.id == image_id
        ).first()
        
        return fresh_image
    except Exception as e:
        session.rollback()
        raise Exception(f"Error adding image: {str(e)}")
    finally:
        session.close()

def get_images_by_property_metadata_id(property_metadata_id: int) -> List[PropertyImage]:
    """
    Get all images for a specific property using SQLAlchemy ORM
    
    Args:
        property_metadata_id: ID of the property
        
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
            .filter(PropertyImage.property_metadata_id == property_metadata_id)
            .order_by(PropertyImage.created_at.desc())
            .all()
        )
        
        return images
    except Exception as e:
        raise Exception(f"Error retrieving images: {str(e)}")
    finally:
        session.close()

def get_images_by_category(property_metadata_id: int, category: str) -> List[PropertyImage]:
    """
    Get all images for a specific property and category
    
    Args:
        property_metadata_id: ID of the property
        category: Image category (e.g., 'Kitchen', 'Bathroom')
        
    Returns:
        List[PropertyImage]: List of image records matching the property and category
        
    Raises:
        Exception: If there was an error retrieving images
    """
    session = Session()
    try:
        # Query using SQLAlchemy ORM
        images = (
            session.query(PropertyImage)
            .filter(
                PropertyImage.property_metadata_id == property_metadata_id,
                PropertyImage.category == category
            )
            .order_by(PropertyImage.created_at.desc())
            .all()
        )
        
        return images
    except Exception as e:
        raise Exception(f"Error retrieving images by category: {str(e)}")
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
            if key in ["property_metadata_id", "category", "source_image_url", "generated_image_url", "state"] and hasattr(image, key):
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

def upsert_image(property_image: PropertyImage) -> Tuple[PropertyImage, bool]:
    # Call the batch upsert function with a single item
    results = upsert_images([property_image])
    return results[0] if results else (None, False)
    
def upsert_images(property_images: List[PropertyImage]) -> List[Tuple[PropertyImage, bool]]:
    """
    Batch upsert (update or insert) multiple property images based on source_image_url as the unique key
    
    Args:
        property_images: List of PropertyImage objects to upsert
        
    Returns:
        List[Tuple[PropertyImage, bool]]: List of (fresh_image, is_new) tuples where:
            - fresh_image is a fresh PropertyImage object loaded from the database
            - is_new is True if a new record was created, False if an existing one was updated
        
    Raises:
        Exception: If there was an error upserting the images
    """
    if not property_images:
        return []
        
    # Validate that all images have required fields
    for image in property_images:
        if not image.source_image_url:
            raise ValueError("source_image_url is required for upsert operation")
        if not image.property_metadata_id:
            raise ValueError("property_metadata_id is required for upsert operation")
    
    session = Session()
    try:
        # Extract all source_image_urls for batch querying
        source_urls = [image.source_image_url for image in property_images]
        
        # Batch query for existing images
        existing_images = session.query(PropertyImage).filter(
            PropertyImage.source_image_url.in_(source_urls)
        ).all()
        
        # Create a lookup dict for faster processing
        existing_image_dict = {image.source_image_url: image for image in existing_images}
        
        # Track which images are new vs. updated
        new_images = []
        updated_image_ids = []
        result_records = []
        
        for property_image in property_images:
            is_new = False
            
            if property_image.source_image_url in existing_image_dict:
                # Update existing image
                existing_image = existing_image_dict[property_image.source_image_url]
                
                # Update fields with non-None values
                if property_image.property_metadata_id is not None:
                    existing_image.property_metadata_id = property_image.property_metadata_id
                if property_image.category is not None:
                    existing_image.category = property_image.category
                if property_image.generated_image_url is not None:
                    existing_image.generated_image_url = property_image.generated_image_url
                if property_image.state is not None:
                    existing_image.state = property_image.state
                    
                updated_image_ids.append(existing_image.id)
                
            else:
                # Add new image to session
                session.add(property_image)
                new_images.append(property_image)
                is_new = True
            
            # Track the result for this image (we'll update with fresh data after commit)
            result_records.append((property_image, is_new))
        
        # Commit all changes in one batch
        session.commit()
        
        # Now we need to refresh the records with database values
        final_results = []
        
        for idx, (property_image, is_new) in enumerate(result_records):
            if is_new:
                # For new images, get the fresh record using the ID assigned during commit
                image_id = property_image.id
                fresh_image = session.query(PropertyImage).filter(
                    PropertyImage.id == image_id
                ).first()
            else:
                # For updated images, use the existing image with updated information
                existing_image = existing_image_dict[property_image.source_image_url]
                fresh_image = existing_image
                
            final_results.append((fresh_image, is_new))
            
        return final_results
        
    except Exception as e:
        session.rollback()
        raise Exception(f"Error batch upserting images: {str(e)}")
    finally:
        session.close()