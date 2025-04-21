#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime

# Add the project root directory to the Python path first
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.insert(0, project_root)

# Import after setting up path
import crawlers.redfin.util as util
from database.real_estate.models import PropertyMetadata
from database.real_estate.operations import upsert_property, upsert_images
from crawlers.redfin.extractors.property_metadata_extractor import PropertyMetadataExtractor
from crawlers.redfin.extractors.property_images_extractor import PropertyImagesExtractor

class RedfinContentExtractor:
    def __init__(self):
        self.debug_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "debug_output")
        if not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)
        self.property_metadata_extractor = PropertyMetadataExtractor()
        self.property_images_extractor = PropertyImagesExtractor()
    
    def process_search_page(self, page, url):
        """
        Navigate to a search results page, save its content and return the page object
        
        Args:
            page: Playwright page object
            url (str): The URL to navigate to
            
        Returns:
            Page: The page object after navigation and processing
        """
        # Navigate to the URL and wait for content to load
        # Using the refactored navigate_to_page that includes content saving
        page, html_file, _ = util.navigate_to_page(
            page, 
            url, 
            page_name="search_result_page", 
            debug_dir=self.debug_dir
        )
        
        return page
    
    def process_property_page(self, context, page, card_selector):
        """
        Process a property details page by either:
        1. Clicking on a card selector in the given page to open a new tab, or
        2. Using an already opened property page
        
        Args:
            context: Browser context for creating new pages
            page: Playwright page object containing search results (if clicking on a card)
            card_selector: CSS selector for the property card to click (e.g. '#MapHomeCard_0')
            property_page: Existing property page object (if already opened)
            
        Returns:
            Page: The property page object after processing
        """
        property_page = None
        
        print(f"Looking for property card element with selector '{card_selector}'...")
        try:
            # Wait for the element to be visible
            card = page.wait_for_selector(card_selector, timeout=10000, state='visible')
            
            if card:
                print("Found property card element. Opening in a new tab...")
                with context.expect_page() as new_page_info:
                    # Hold down Meta key (Command on Mac) while clicking to open in a new tab
                    page.click(card_selector, modifiers=['Meta'])
                
                property_page = new_page_info.value
                
                # Bring focus to the newly opened tab
                property_page.bring_to_front()
                print(f"Browser navigated to new tab with URL: {property_page.url}")
                
                # Wait a bit for content to load
                print("Processing property details page...")
                time.sleep(2)
                
                # Extract property data
                property_data = self.extract_property_data(property_page)
                
                # Close the tab if we opened it during this function call
                print("Closing the property details tab")
                property_page.close()
                time.sleep(1)
                
                print("Property details page processed successfully")
                return property_page
            else:
                print(f"Property card element with selector '{card_selector}' was not found on the page")
                return None
        except Exception as e:
            print(f"Error when trying to open property details: {str(e)}")
            return None
    
    def extract_property_data(self, property_page):
        """
        Extract property data from the property details page
        
        Args:
            property_page: Playwright page object containing property details
            
        Returns:
            dict: Dictionary containing property information
        """
        print("Extracting property data...")
        
        try:
            # Extract property metadata (address, price, pending date)
            property_metadata = self.property_metadata_extractor.extract_property_metadata(property_page)

            # Extract property images using the dedicated extractor
            property_images = self.property_images_extractor.extract_property_images(property_page)
            
            # Save to database
            db_result = self.upsert_to_db(property_metadata, property_images)
            
            return db_result
            
        except Exception as e:
            print(f"Error extracting property data: {str(e)}")
            return None
    
    def upsert_to_db(self, property_metadata, property_images):
        """
        Save property metadata and images to database using upsert operations
        
        Args:
            property_metadata: PropertyMetadata object to save
            property_images: List of PropertyImage objects to save
            
        Returns:
            tuple: (property_metadata, property_images) if saved successfully, None otherwise
        """
        # Check if property_images is empty
        if not property_images:
            print("No property images to save. Skipping database operation.")
            return None
            
        try:
            print("Saving property metadata to database...")
            # Upsert the property metadata first to get an ID
            saved_property, is_new = upsert_property(property_metadata)
            
            if is_new:
                print(f"Created new property record with ID: {saved_property.id}")
            else:
                print(f"Updated existing property record with ID: {saved_property.id}")
                
            print(f"Saving {len(property_images)} images to database...")
            
            # Update each image with the property_metadata_id
            for image in property_images:
                image.property_metadata_id = saved_property.id
            
            # Batch upsert images to database
            saved_images = upsert_images(property_images)
            
            return (saved_property, saved_images)
            
        except Exception as e:
            print(f"Error saving data to database: {str(e)}")
            return None
    
    def start(self, url):
        """
        Open the specified Redfin URL and extract its HTML content.
        Also clicks on the first property card in a new tab.
        
        Args:
            url (str): The Redfin URL to open
            
        Returns:
            str: The HTML content of the page
        """
        browser, context, playwright = util.launch_browser(headless=False, debug_dir=self.debug_dir)
        
        try:
            page = context.new_page()
            
            # Process the search results page using the new method
            page = self.process_search_page(page, url)
            
            # Use the updated process_property_page method to handle clicking and processing
            self.process_property_page(context, page=page, card_selector='#MapHomeCard_1')
            
            # Here you can do additional processing with property_page data if needed
            # For example, you could extract specific information from the property page
            
        except Exception as e:
            print(f"Error extracting content: {str(e)}")
            return None
            
        finally:
            browser.close()
            playwright.stop()

if __name__ == "__main__":
    # Redfin URL for Snohomish County with specified filters
    url = "https://www.redfin.com/county/2/WA/Snohomish-County/filter/sort=hi-price,property-type=house+condo+townhouse,min-year-built=2025,status=contingent+pending,mr=5:118"
    
    extractor = RedfinContentExtractor()
    extractor.start(url)