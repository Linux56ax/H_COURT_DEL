from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup

court_url = "https://delhihighcourt.nic.in/app/case-type-status-details/eyJpdiI6ImpzQ0pkZVpYUmN0dk1IcTR3d0wzS2c9PSIsInZhbHVlIjoiYWNGZzBwYk1ha1A3K1JwMnRTQUFTUT09IiwibWFjIjoiZDllMWQxNWI5MzlmMDA3ZTkwOTY5YTZhZjg4ZTNmNWU0Yzk2YTdiODRhNGY0NTY5NjQ3YzUyOTJhMDQ4N2RjOCIsInRhZyI6IiJ9/eyJpdiI6Imh6NTlrdUd3MzFJYlM3bDd3UThIdUE9PSIsInZhbHVlIjoic0JXZXFIaWx6WEtyRkNxL3hYZkVIUT09IiwibWFjIjoiMmZjN2QyMjAyZDI0MjZkNDBhOWY5NzE1YTE1ZmQ3MDE0NzJmYTgyZjBiMjkyMmY3YTljZmQ3Y2JjZTljNmU3YSIsInRhZyI6IiJ9/eyJpdiI6Ik91Z1FFZlhJallxYzJDZStXY1VzcUE9PSIsInZhbHVlIjoiTEVteE9aMDRUTGtHYWJTMGQwOGc4dz09IiwibWFjIjoiODRmOGFjODg1MGMzNWMwOGZkMGRmZDA3YjJjYWExYTdlMDBhMThkOTRkODZlZDIzYTg0NzYwOGE0Y2FjYzY1ZCIsInRhZyI6IiJ9"
def submit_order_search(court_url: str):
    
    with sync_playwright() as p:
        browser = None
        try:
            # Try to launch a Chromium browser first
            browser = p.chromium.launch(headless=True)
        except Exception as e:
            print(f"Error launching Chromium: {e}")
            try:
                # Fallback to Firefox if Chromium fails
                browser = p.firefox.launch(headless=True)
            except Exception as e:
                print(f"Error launching Firefox: {e}")
                print("Could not initialize any browser.")
                return None

        if not browser:
            return None

        page: Page = browser.new_page()

        try:
            #print(f"Navigating to {court_url}...")
            page.goto(court_url)
            print("Page loaded successfully.")


            print("Waiting for results to load (network idle)...")
            page.wait_for_load_state('networkidle')
            print("Results page loaded successfully.")

            # Get the page content
            page_html = page.content()
            return page_html

        except Exception as e:
            print(f"An error occurred during automation: {e}")
            return None
        finally:
            if browser:
                browser.close()
                print("Browser closed.")




#Function to extract the Case URL file for orderds
def extract_url(result:str):
    soup = BeautifulSoup(result, 'html.parser')
    #result_url=soup.find('a', href=lambda href: href and href.startswith("https://delhihighcourt.nic.in/app/showlogo/"))
    result=soup.find_all(id='caseTable')
"""    if result_url:
        return result_url.get('href')"""

Html=submit_order_search(court_url)
print(Html)
print(extract_url(Html))