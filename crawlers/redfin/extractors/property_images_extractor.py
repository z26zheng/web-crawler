#!/usr/bin/env python3
import os
import sys
import time

# Add the project root directory to the Python path first
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.insert(0, project_root)

class PropertyImagesExtractor:
    def __init__(self):
        pass
    
    def fetch_images(self, property_page, filter_name):
        """
        Fetches images for a specific filter category
        
        Args:
            property_page: Playwright page object
            filter_name: The name of the filter (e.g. 'Kitchen', 'Bathroom')
        
        Returns:
            list: List of image URLs for the filter (currently empty)
        """
        print(f"Fetching images for filter: {filter_name}")
        time.sleep(1)  # Sleep for 1 second as requested
        return []
    
    def open_photo_gallery(self, property_page):
        """
        Open the photo gallery by clicking on the photos button
        
        Args:
            property_page: Playwright page object
            
        Returns:
            bool: True if gallery was opened successfully, False otherwise
        """
        try:
            # Find and click on the photos button
            photos_button_selector = '[data-buttonenum="photos"]'
            
            # Wait for the button to be visible and clickable
            property_page.wait_for_selector(photos_button_selector, state='visible', timeout=10000)
            
            # Click on the photos button to open the gallery
            property_page.click(photos_button_selector)
            
            # Wait for gallery to load and stabilize
            property_page.wait_for_timeout(3000)
            
            # Wait for the dialog wrapper to appear (common container for modals in Redfin)
            dialog_wrapper_selector = '.DialogWrapper'
            property_page.wait_for_selector(dialog_wrapper_selector, state='visible', timeout=10000)
            
            # Force reload of DOM content to ensure we're working with the updated DOM
            property_page.evaluate("document.body.innerHTML")
            
            return True
        except Exception as e:
            print(f"Error opening photo gallery: {str(e)}")
            return False
    
    def close_gallery(self, property_page):
        """
        Close the gallery by pressing Escape key
        
        Args:
            property_page: Playwright page object
        """
        try:
            property_page.keyboard.press('Escape')
            property_page.wait_for_timeout(1000)  # Wait for gallery to close
        except Exception as e:
            print(f"Error closing gallery: {str(e)}")
    
    def find_filter_bar(self, property_page):
        """
        Find the photo filter bar in the gallery
        
        Args:
            property_page: Playwright page object
            
        Returns:
            tuple: (bool, str) - (whether filter bar was found, filter bar selector)
        """
        filter_bar_selector = '.DialogWrapper .PhotoFilterBar'
        
        try:
            property_page.wait_for_selector(filter_bar_selector, state='visible', timeout=5000)
            return True, filter_bar_selector
        except Exception as e:
            print(f"Photo filter bar not found: {str(e)}")
            return False, filter_bar_selector
    
    def process_filter_tabs(self, property_page, filter_bar_selector):
        """
        Process each filter tab in the gallery
        
        Args:
            property_page: Playwright page object
            filter_bar_selector: CSS selector for the filter bar
            
        Returns:
            list: Combined list of image URLs from all filters
        """
        all_image_urls = []
        
        # First, count how many filter tabs there are
        filter_options_selector = f'{filter_bar_selector} > span'
        filter_count = property_page.evaluate(f"""() => {{
            return document.querySelectorAll('{filter_options_selector}').length;
        }}""")
        
        print(f"Found {filter_count} filter tabs")
        
        # Process each filter, starting from index 1 (skipping "All")
        for i in range(1, filter_count):
            try:
                filter_name, success = self.click_filter_tab(
                    property_page, filter_options_selector, i
                )
                
                if success:
                    # Call the fetch_images method for this filter
                    filter_images = self.fetch_images(property_page, filter_name)
                    all_image_urls.extend(filter_images)
                    
            except Exception as e:
                print(f"Error processing filter tab {i}: {str(e)}")
                
        return all_image_urls
    
    def click_filter_tab(self, property_page, filter_options_selector, index):
        """
        Click on a specific filter tab and get its name
        
        Args:
            property_page: Playwright page object
            filter_options_selector: CSS selector for filter options
            index: Index of the filter tab to click
            
        Returns:
            tuple: (filter_name, success) - (name of the filter, whether click was successful)
        """
        # Get fresh reference to the filter element using JavaScript
        filter_name = property_page.evaluate(f"""(index) => {{
            const filters = document.querySelectorAll('{filter_options_selector}');
            if (filters.length > index) {{
                const filter = filters[index];
                const nameElem = filter.querySelector('p.font-body-xsmall');
                return nameElem ? nameElem.textContent.trim() : `Filter ${{index}}`;
            }}
            return `Filter ${{index}}`;
        }}""", index)
        
        print(f"Processing filter tab {index}: {filter_name}")
        
        # Click the filter tab using JavaScript to avoid stale element references
        property_page.evaluate(f"""(index) => {{
            const filters = document.querySelectorAll('{filter_options_selector}');
            if (filters.length > index) {{
                filters[index].click();
            }}
        }}""", index)
        
        # Wait a moment for the filter to apply
        property_page.wait_for_timeout(1000)
        
        return filter_name, True
    
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
        image_urls = []
        
        try:
            # Step 1: Open the photo gallery
            if not self.open_photo_gallery(property_page):
                return []
                
            # Step 2: Find the filter bar
            has_filter_bar, filter_bar_selector = self.find_filter_bar(property_page)
            
            # Step 3: Process filter tabs if filter bar exists
            if has_filter_bar:
                image_urls = self.process_filter_tabs(property_page, filter_bar_selector)
            
            # Step 4: Close the gallery
            self.close_gallery(property_page)
            
            return image_urls
            
        except Exception as e:
            print(f"Error extracting property images: {str(e)}")
            
            # Try to close the gallery if it's open before returning
            self.close_gallery(property_page)
            
            return image_urls
