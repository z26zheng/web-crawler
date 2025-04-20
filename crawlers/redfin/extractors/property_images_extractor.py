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
            list: List of image URLs for the filter
        """
        print(f"Fetching images for filter: {filter_name}")
        image_urls = []
        
        try:
            # Wait for image cards to be present in the DOM - using a more specific selector
            image_cards_selector = '[id^="MB-image-card-"]'
            property_page.wait_for_selector(image_cards_selector, timeout=5000)
            
            # Get all image cards using Playwright's query_selector_all method
            image_cards = property_page.query_selector_all(image_cards_selector)
            print(f"Found {len(image_cards)} image cards for filter: {filter_name}")
            
            # Extract image URLs from each card using Playwright's native methods
            for i, card in enumerate(image_cards):
                # Find the image within the card
                img = card.query_selector('img.img-card')
                if img:
                    # Get the src attribute using Playwright's native getAttribute method
                    image_url = img.get_attribute('src')
                    if image_url:
                        print(f"Image {i}: {image_url}")
                        image_urls.append(image_url)
                
            return image_urls
        except Exception as e:
            print(f"Error extracting images for filter {filter_name}: {str(e)}")
            return image_urls
    
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
            
            # Use Playwright's built-in retry mechanism with auto-waiting
            # This will automatically retry until the element is visible and stable
            photos_button = property_page.locator(photos_button_selector)
            
            # Wait for the button to be visible and clickable with proper state
            photos_button.wait_for(state='visible', timeout=10000)
            
            # Click on the photos button to open the gallery
            photos_button.click()
            
            # Wait for gallery to appear using a more reliable approach
            # Look for the dialog wrapper which contains the gallery
            dialog_wrapper = property_page.locator('.DialogWrapper')
            dialog_wrapper.wait_for(state='visible', timeout=10000)
            
            print("Successfully opened photo gallery")
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
            
            # Wait for gallery to disappear with a more reliable approach
            dialog_wrapper = property_page.locator('.DialogWrapper')
            dialog_wrapper.wait_for(state='hidden', timeout=5000)
            print("Gallery closed successfully")
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
            # Use locator API for better retry handling
            filter_bar = property_page.locator(filter_bar_selector)
            
            # Wait with polling to detect when it's available
            is_visible = filter_bar.is_visible(timeout=5000)
            return is_visible, filter_bar_selector
        except Exception as e:
            print(f"Photo filter bar not found: {str(e)}")
            return False, filter_bar_selector
    
    def process_filter_tabs(self, property_page, filter_bar_selector):
        """
        Process each filter tab and extract images using Playwright-native methods
        
        Args:
            property_page: Playwright page object
            filter_bar_selector: CSS selector for the filter bar
            
        Returns:
            list: List of image URLs from all filter tabs
        """
        print("Processing filter tabs...")
        all_image_urls = []
        
        try:
            # Wait for the filter options to be visible
            filter_options_selector = f"{filter_bar_selector} > span"
            property_page.wait_for_selector(filter_options_selector, timeout=5000)
            
            # Get all filter tabs
            filter_tabs = property_page.query_selector_all(filter_options_selector)
            print(f"Found {len(filter_tabs)} filter tabs")
            
            # Process each filter tab
            for i in range(len(filter_tabs)):
                # Click on the filter tab
                filter_name, success = self.click_filter_tab(property_page, filter_options_selector, i)
                
                if success:
                    # After clicking, wait for images to load
                    property_page.wait_for_timeout(1000)
                    
                    # Extract images from the current filter tab
                    tab_images = self.fetch_images(property_page, filter_name)
                    print(f"Found {len(tab_images)} images in filter tab '{filter_name}'")
                    
                    # Add the images to our list
                    all_image_urls.extend(tab_images)
            
            return all_image_urls
            
        except Exception as e:
            print(f"Error processing filter tabs: {str(e)}")
            
            # If there was an error with tabs, try to extract images from the current view
            fallback_images = self.fetch_images(property_page, "Fallback")
            print(f"Fallback: extracted {len(fallback_images)} images from current view")
            return fallback_images
    
    def click_filter_tab(self, property_page, filter_options_selector, index):
        """
        Click on a filter tab using Playwright-native methods
        
        Args:
            property_page: Playwright page object
            filter_options_selector: CSS selector for filter options
            index: Index of the tab to click
            
        Returns:
            tuple: (filter_name, success) - Name of the filter and whether click was successful
        """
        try:
            # Re-query the filter tabs to ensure we have the latest DOM
            filter_tabs = property_page.query_selector_all(filter_options_selector)
            
            if index < len(filter_tabs):
                # Get the tab element
                tab = filter_tabs[index]
                
                # Get the tab name before clicking
                filter_name = tab.text_content().strip() if tab.text_content() else f"Tab {index + 1}"
                print(f"Clicking on filter tab: '{filter_name}'")
                
                # Click on the tab
                tab.click()
                
                # Wait for any animations or loading to complete
                property_page.wait_for_timeout(1000)
                
                return filter_name, True
            else:
                print(f"Filter tab index {index} out of range. Only {len(filter_tabs)} tabs found.")
                return f"Tab {index + 1}", False
                
        except Exception as e:
            print(f"Error clicking on filter tab {index}: {str(e)}")
            return f"Tab {index + 1}", False
    
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
