#!/usr/bin/env python3
import os
import time
import shutil
from datetime import datetime
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext

def clean_debug_directory(debug_dir):
    """
    Clean the debug directory by removing all existing files
    
    Args:
        debug_dir (str): Path to the debug directory to clean
    """
    if os.path.exists(debug_dir):
        print(f"Cleaning debug directory: {debug_dir}")
        # Remove all files in the directory
        for filename in os.listdir(debug_dir):
            file_path = os.path.join(debug_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Error while cleaning debug directory: {str(e)}")
    else:
        # Create the directory if it doesn't exist
        os.makedirs(debug_dir)

def launch_browser(headless: bool = False, debug_dir: str = None) -> tuple[Browser, BrowserContext, sync_playwright]:
    """
    Launch a browser configured for Redfin with anti-bot protection countermeasures
    
    Args:
        headless (bool): Whether to run the browser in headless mode
        debug_dir (str, optional): Debug directory to clean before browser launch
        
    Returns:
        tuple: (Browser, BrowserContext, playwright) - The launched browser, its context, and playwright instance
    """
    # Clean the debug directory if provided
    if debug_dir:
        clean_debug_directory(debug_dir)
        
    playwright = sync_playwright().start()
    
    # Launch with options to better handle websites with anti-bot measures
    browser = playwright.chromium.launch(
        headless=headless,
        args=['--disable-blink-features=AutomationControlled']
    )
    
    # Create a context with more realistic browser parameters
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        viewport={'width': 1280, 'height': 800},
        device_scale_factor=2,
        locale='en-US',
        timezone_id='America/Los_Angeles',
    )
    
    # Add cookies to appear more like a regular browser session
    context.add_cookies([{
        'name': 'visitor_id',
        'value': '12345-visitor-id',
        'domain': '.redfin.com',
        'path': '/',
    }])
    
    return browser, context, playwright

def navigate_to_page(page: Page, url: str, page_name: str = None, debug_dir: str = None, scroll_down: bool = True) -> tuple[Page, str, str]:
    """
    Navigate to a URL, wait for it to load, optionally scroll down, and save debug content
    
    Args:
        page (Page): Playwright page object
        url (str): URL to navigate to
        page_name (str, optional): Name to use for the debug files. If None, debug files won't be saved
        debug_dir (str, optional): Directory to save debug files. Defaults to 'debug_output' in script directory
        scroll_down (bool): Whether to scroll down the page after loading
        
    Returns:
        tuple: (page, html_file_path, screenshot_file_path) - The page object and paths to saved files (if any)
    """
    print(f"Navigating to {url}")
    
    # Use 'domcontentloaded' to avoid long waits for complete network idle
    page.goto(url, wait_until="domcontentloaded", timeout=100000)
    
    # Wait for content to load
    print("Waiting for page content to fully load...")
    time.sleep(5)
    
    # Scroll down to simulate user behavior and trigger lazy loading
    if scroll_down:
        for _ in range(3):
            page.mouse.wheel(0, 300)
            time.sleep(1)
    
    # Save debug content if page_name is provided
    html_file = None
    screenshot_file = None
    
    if page_name:
        html_file, screenshot_file = _save_debug_content(page, page_name, debug_dir)
    
    return page, html_file, screenshot_file

def _save_debug_content(page: Page, page_name: str, debug_dir: str = None) -> tuple[str, str]:
    """
    Save the HTML content and screenshot of a page for debugging (internal function)
    
    Args:
        page (Page): Playwright page object
        page_name (str): Name to use for the debug files
        debug_dir (str, optional): Directory to save debug files. Defaults to 'debug_output' in script directory
        
    Returns:
        tuple: (html_file_path, screenshot_file_path) - Paths to the saved files
    """
    if debug_dir is None:
        debug_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_output")
    
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
    
    # Save HTML content with no timestamp
    content = page.content()
    html_file = os.path.join(debug_dir, f"redfin_{page_name}.html")
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    # Take a screenshot with error handling
    screenshot_file = os.path.join(debug_dir, f"redfin_{page_name}.png")
    try:
        page.screenshot(path=screenshot_file, full_page=True, timeout=30000)
        print(f"Screenshot saved to {screenshot_file}")
    except Exception as e:
        print(f"Warning: Could not capture screenshot: {str(e)}")
        screenshot_file = None
    
    print(f"HTML content saved to {html_file}")
    
    return html_file, screenshot_file