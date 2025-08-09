from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup

court_url = "https://delhihighcourt.nic.in/app/case-type-status-details/eyJpdiI6InNzckhSNEIvMDBGNExQVW1QR2htV3c9PSIsInZhbHVlIjoiTTlpMVlHeUJzWlNuOVRIaTRMaHBpdz09IiwibWFjIjoiYzhhNTg5ZmVlMTE2ZjM3ZThjMThhMmQ3Zjg2NDg2YTc4MGU2YjViYzg1NjJkNWJjMjQxYmY1ZWU2YzVkODhhMyIsInRhZyI6IiJ9/eyJpdiI6Ii90Yk5JWnhrZGVyNGJDd3MzYXJYZFE9PSIsInZhbHVlIjoicmVjM2N1M2p4c2I0cUNUbEgvbE56dz09IiwibWFjIjoiYjY1ZDFjYTQwMzM1ZTkyMzBjYzU0OTI4ODM3ZWJmNzVjNjU0ZDNhOTFiZmEzNjQ3NDhkNTQ4MTZjNGI2ZDcxNiIsInRhZyI6IiJ9/eyJpdiI6InhpcVFhRzkySkdWVk9SeStMSWE0U2c9PSIsInZhbHVlIjoiZUhiWXBHUGhvcjdnS2ZKVVQxWWdpQT09IiwibWFjIjoiODRiYjM3ZDcxMjhlYmVjOTI2YmFhY2E4OGMzM2U5MmQwMmQzZmU3MWUwOTA0ZWFlNTU5YWU0OTZhZTBhMTI0OCIsInRhZyI6IiJ9"
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
    all_text_content = soup.stripped_strings
    extracted_dates = []
    # Iterate through all the text strings found by BeautifulSoup
    for text_string in all_text_content:
    # Split the string by spaces to get individual words or parts
        words = text_string.split()
        for word in words:
            # Manually check if the word is a date without a separate function
            # This is the combined logic from the old is_date function.
            if (len(word) == 10 and 
                word[2] == '/' and 
                word[5] == '/' and 
                word[:2].isdigit() and 
                word[3:5].isdigit() and 
                word[6:].isdigit()):
                extracted_dates.append(word)

    result_url=soup.find_all('a', href=lambda href: href and href.startswith("https://delhihighcourt.nic.in/app/showlogo/"))
    urls = []
    for _ in result_url:
        urls.append(_.get('href'))
    if result_url:
        return urls, extracted_dates

Html=submit_order_search(court_url)
# print(Html)
print(extract_url(Html))




