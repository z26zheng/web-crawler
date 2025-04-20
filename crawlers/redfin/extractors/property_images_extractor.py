#!/usr/bin/env python3
import os
import sys

# Add the project root directory to the Python path first
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.insert(0, project_root)

class PropertyImagesExtractor:
    def __init__(self):
        pass
    
    def extract_property_images(self, property_page):
        """
        Extract property images by clicking on the photo gallery button and
        gathering image URLs from the opened gallery
        
        Args:
            property_page: Playwright page object containing property details
            
        Returns:
            list: List of image URLs for the property
        """
        print("Extracting property images...")
        image_urls = set()  # Using a set to avoid duplicate URLs
        
        # Find and click on the photos button
        photos_button_selector = '[data-buttonenum="photos"]'
        print(f"Looking for photos button with selector: {photos_button_selector}")
        
        # Wait for the button to be visible and clickable
        property_page.wait_for_selector(photos_button_selector, state='visible', timeout=5000)
        
        # Click on the photos button to open the gallery
        print("Clicking on the photos button to open the gallery...")
        property_page.click(photos_button_selector)
        
        # Wait for gallery to load and stabilize
        print("Waiting for gallery to load...")
        property_page.wait_for_timeout(2000)
        
        # Wait for the media viewer to be visible
        media_viewer_selector = '.MediaViewerModal'
        property_page.wait_for_selector(media_viewer_selector, state='visible', timeout=5000)
        