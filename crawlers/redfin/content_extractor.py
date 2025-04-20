#!/usr/bin/env python3
import os
import time
from . import util

class RedfinContentExtractor:
    def __init__(self):
        self.debug_dir = os.path.join(os.path.dirname(__file__), "debug_output")
        if not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)
    
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
    
    def process_property_page(self, context, property_page):
        """
        Process a property details page using an existing page object
        
        Args:
            context: Browser context for creating new pages
            property_page: Existing page object
            
        Returns:
            Page: The page object after processing
        """
        if property_page:
            print("Processing property details page...")
            # No navigation needed, just capture the content
            property_page, _, _ = util.navigate_to_page(
                property_page,
                property_page.url,
                page_name="property_details_page",
                debug_dir=self.debug_dir,
                scroll_down=False  # Don't scroll again as this is already loaded
            )
            print("Property details page processed successfully")
            return property_page
        
        print("No property page provided to process")
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
            
            # Try to find and click on the MapHomeCard_0 element in a new tab
            print("Looking for property card element with ID 'MapHomeCard_0'...")
            
            try:
                # Wait for the element to be visible
                card = page.wait_for_selector('#MapHomeCard_0', timeout=10000, state='visible')
                
                if card:
                    print("Found property card element. Opening in a new tab...")
                    with context.expect_page() as new_page_info:
                        # Hold down Meta key (Command on Mac) while clicking to open in a new tab
                        page.click('#MapHomeCard_0', modifiers=['Meta'])
                    
                    property_page = new_page_info.value
                    
                    # Process the property details page
                    property_page = self.process_property_page(context, property_page=property_page)
                else:
                    print("Property card element was not found on the page")
            except Exception as e:
                print(f"Error when trying to open property details: {str(e)}")
                print("Continuing with the search results page content only")
            
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