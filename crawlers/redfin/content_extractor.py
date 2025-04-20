#!/usr/bin/env python3
import os
import time
# Fix import to work in both direct execution and package import scenarios
try:
    # When imported as part of a package
    from . import util
except ImportError:
    # When run directly
    import util

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
            # Initialize property data dictionary
            property_data = {}
            
            # Extract property metadata (address, etc.)
            metadata = self.extract_property_metadata(property_page)
            if metadata:
                property_data.update(metadata)
                print(f"Extracted property metadata: {metadata}")
            
            # Extract property statistics (price, beds, baths, sqft)
            stats = self.extract_property_statistics(property_page)
            if stats:
                property_data.update(stats)
                print(f"Extracted property statistics: {stats}")
            
            return property_data
            
        except Exception as e:
            print(f"Error extracting property data: {str(e)}")
            return None
            
    def extract_property_statistics(self, property_page):
        """
        Extract property statistics including price, beds, baths, and square footage
        
        Args:
            property_page: Playwright page object containing property details
            
        Returns:
            dict: Dictionary containing property statistics
        """
        print("Extracting property statistics...")
        stats = {}
        
        try:
            # Find the main stats container
            stats_container = property_page.query_selector('.home-main-stats-variant')
            if not stats_container:
                print("Property stats container not found")
                return stats
                
            # Extract price
            price_element = stats_container.query_selector('[data-rf-test-id="abp-price"] .statsValue')
            if price_element:
                price_text = price_element.inner_text().strip()
                # Remove non-numeric characters from the price and convert to float
                price_numeric = ''.join(c for c in price_text if c.isdigit() or c == '.')
                try:
                    stats['price'] = float(price_numeric) if price_numeric else None
                    stats['price_text'] = price_text
                    print(f"Extracted price: {price_text}")
                except ValueError:
                    print(f"Could not convert price '{price_text}' to a number")
            
            return stats
            
        except Exception as e:
            print(f"Error extracting property statistics: {str(e)}")
            return {}
    
    def extract_property_metadata(self, property_page):
        """
        Extract property metadata including address from the property details page
        
        Args:
            property_page: Playwright page object containing property details
            
        Returns:
            dict: Dictionary containing property metadata
        """
        print("Extracting property metadata...")
        metadata = {}
        
        try:
            # Extract address from the header element
            # Look for the address header element
            address_header = property_page.query_selector('header.address')
            if address_header:
                # Extract street address
                street_element = address_header.query_selector('.street-address')
                if street_element:
                    street_address = street_element.inner_text().strip().replace(',', '')
                    metadata['street_address'] = street_address
                    print(f"Extracted street address: {street_address}")
                
                # Extract city, state, zip
                city_state_zip_element = address_header.query_selector('.bp-cityStateZip')
                if city_state_zip_element:
                    city_state_zip_text = city_state_zip_element.inner_text().strip()
                    # Parse city, state, zip components
                    parts = city_state_zip_text.split(',')
                    if len(parts) > 0:
                        metadata['city'] = parts[0].strip()
                    
                    if len(parts) > 1:
                        state_zip_parts = parts[1].strip().split()
                        if len(state_zip_parts) > 0:
                            metadata['state'] = state_zip_parts[0].strip()
                        
                        if len(state_zip_parts) > 1:
                            metadata['zip_code'] = state_zip_parts[1].strip()
                    
                    print(f"Extracted city/state/zip: {city_state_zip_text}")
                
                # Combine components into full address
                if 'street_address' in metadata and 'city' in metadata and 'state' in metadata and 'zip_code' in metadata:
                    metadata['full_address'] = f"{metadata['street_address']}, {metadata['city']}, {metadata['state']} {metadata['zip_code']}"
                    print(f"Full address: {metadata['full_address']}")
            else:
                print("Address header element not found on the page")
            
            return metadata
            
        except Exception as e:
            print(f"Error extracting property metadata: {str(e)}")
            return {}

    
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
            property_page = self.process_property_page(context, page=page, card_selector='#MapHomeCard_0')
            
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