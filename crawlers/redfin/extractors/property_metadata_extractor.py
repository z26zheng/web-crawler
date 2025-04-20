#!/usr/bin/env python3
import os
import sys
from datetime import datetime

# Add the project root directory to the Python path first
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.insert(0, project_root)

# Import after setting up path
from database.real_estate.models import PropertyMetadata

class PropertyMetadataExtractor:
    def __init__(self):
        pass
    
    def extract_property_price(self, property_page):
        """
        Extract property price and convert to integer
        
        Args:
            property_page: Playwright page object containing property details
            
        Returns:
            int: Property price as integer, None if not found
        """
        print("Extracting property price...")
        try:
            # Find the main stats container
            stats_container = property_page.query_selector('.home-main-stats-variant')
            if not stats_container:
                print("Property stats container not found")
                return None
                
            # Extract price
            price_element = stats_container.query_selector('[data-rf-test-id="abp-price"] .statsValue')
            if price_element:
                price_text = price_element.inner_text().strip()
                # Remove non-numeric characters from the price and convert to integer
                price_numeric = ''.join(c for c in price_text if c.isdigit())
                try:
                    price = int(price_numeric) if price_numeric else None
                    print(f"Extracted price: {price} from {price_text}")
                    return price
                except ValueError:
                    print(f"Could not convert price '{price_text}' to a number")
                    return None
            
            return None
            
        except Exception as e:
            print(f"Error extracting property price: {str(e)}")
            return None
    
    def extract_property_address(self, property_page):
        """
        Extract property address components
        
        Args:
            property_page: Playwright page object containing property details
            
        Returns:
            dict: Dictionary containing address components
        """
        print("Extracting property address...")
        address_data = {}
        
        try:
            # Look for the address header element
            address_header = property_page.query_selector('header.address')
            if address_header:
                # Extract street address
                street_element = address_header.query_selector('.street-address')
                if street_element:
                    street_address = street_element.inner_text().strip().replace(',', '')
                    address_data['street_address'] = street_address
                    print(f"Extracted street address: {street_address}")
                
                # Extract city, state, zip
                city_state_zip_element = address_header.query_selector('.bp-cityStateZip')
                if city_state_zip_element:
                    city_state_zip_text = city_state_zip_element.inner_text().strip()
                    # Parse city, state, zip components
                    parts = city_state_zip_text.split(',')
                    if len(parts) > 0:
                        address_data['city'] = parts[0].strip()
                    
                    if len(parts) > 1:
                        state_zip_parts = parts[1].strip().split()
                        if len(state_zip_parts) > 0:
                            address_data['state'] = state_zip_parts[0].strip()
                        
                        if len(state_zip_parts) > 1:
                            address_data['zip_code'] = state_zip_parts[1].strip()
                    
                    print(f"Extracted city/state/zip: {city_state_zip_text}")
                
                # Combine components into full address
                if 'street_address' in address_data and 'city' in address_data and 'state' in address_data and 'zip_code' in address_data:
                    address_data['full_address'] = f"{address_data['street_address']}, {address_data['city']}, {address_data['state']} {address_data['zip_code']}"
                    print(f"Full address: {address_data['full_address']}")
            else:
                print("Address header element not found on the page")
                
            return address_data
            
        except Exception as e:
            print(f"Error extracting property address: {str(e)}")
            return {}
    
    def extract_property_pending_date(self, property_page):
        """
        Extract property pending date in SQL-compatible format (YYYY-MM-DD)
        
        Args:
            property_page: Playwright page object containing property details
            
        Returns:
            str: SQL DATE compatible string (YYYY-MM-DD), None if not found
        """
        print("Extracting property pending date...")
        try:
            # Extract pending date
            pending_element = property_page.query_selector('.ListingStatusBannerSection')
            if pending_element:
                pending_text = pending_element.inner_text().strip()
                # Check for "PENDING ON" text pattern
                if "PENDING ON" in pending_text:
                    # Extract the date portion after "PENDING ON"
                    date_portion = pending_text.split("PENDING ON")[1].strip()
                    
                    # Convert to SQL DATE format (YYYY-MM-DD)
                    # Assuming date_portion is in a format like "Mar 22, 2025"
                    try:
                        parsed_date = datetime.strptime(date_portion, "%b %d, %Y")
                        sql_date = parsed_date.strftime("%Y-%m-%d")
                        print(f"Extracted pending date: {sql_date} from {date_portion}")
                        return sql_date
                    except ValueError as e:
                        print(f"Could not parse date '{date_portion}': {str(e)}")
                        return None
            
            print("Pending status element not found on the page")
            return None
            
        except Exception as e:
            print(f"Error extracting property pending date: {str(e)}")
            return None
    
    def extract_source_url(self, property_page):
        """
        Extract the absolute URL of the property page as a string
        
        Args:
            property_page: Playwright page object containing property details
            
        Returns:
            str: Property page URL as a string, None if not available
        """
        print("Extracting property source URL...")
        try:
            # Get the current URL of the property page
            url = property_page.url
            
            if url and url.strip():
                # Ensure it's an absolute URL
                if url.startswith('http'):
                    print(f"Extracted property URL: {url}")
                    return url
                else:
                    # If somehow we got a relative URL, make it absolute (unlikely in Playwright)
                    base_url = "www.redfin.com"
                    absolute_url = f"{base_url.rstrip('/')}/{url.lstrip('/')}"
                    print(f"Converted relative URL to absolute: {absolute_url}")
                    return absolute_url
            else:
                print("Property URL is empty or not available")
                return None
                
        except Exception as e:
            print(f"Error extracting property source URL: {str(e)}")
            return None
    
    def extract_property_metadata(self, property_page):
        """
        Extract property metadata and construct a PropertyMetadata object
        
        Args:
            property_page: Playwright page object containing property details
            
        Returns:
            PropertyMetadata: SQLAlchemy ORM model instance with extracted data
        """
        print("Extracting property metadata...")
        
        try:
            # Extract address data
            address_data = self.extract_property_address(property_page)
            
            # Extract price
            price = self.extract_property_price(property_page)
            
            # Extract pending date
            pending_date = self.extract_property_pending_date(property_page)
            
            # Extract source URL (now as a string)
            source_url = self.extract_source_url(property_page)
            
            # Create the PropertyMetadata object with extracted data
            property_metadata = PropertyMetadata(
                address=address_data,  # JSONB field
                pending_date=pending_date,  # Date field
                price=price,  # Integer field
                source_url=source_url,  # Now stored as string
                status="PENDING" if pending_date else "ACTIVE"  # Set status based on pending_date
            )
            
            print(f"Created PropertyMetadata object {property_metadata.to_dict()}")
            return property_metadata
            
        except Exception as e:
            print(f"Error creating PropertyMetadata object: {str(e)}")
            return None