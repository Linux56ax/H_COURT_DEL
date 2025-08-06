from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup


def submit_case_search(case_type: str, case_number: str, year: str) -> str | None:
    """
    Automates the search for a case on the Delhi High Court website using Playwright.

    Args:
        case_type (str): The type of the case (e.g., "W.P.(C)").
        case_number (str): The case number.
        year (str): The year of the case.

    Returns:
        str | None: The HTML content of the results page if successful, otherwise None.
    """
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
        court_url = "https://delhihighcourt.nic.in/app/get-case-type-status"

        try:
            print(f"Navigating to {court_url}...")
            page.goto(court_url)
            print("Page loaded successfully.")

            # Locate elements using Playwright's locator API
            case_type_element = page.locator('#case_type')
            case_number_element = page.locator('#case_number')
            case_year_element = page.locator('#case_year')
            submit_button_element = page.locator('#search')

            captcha_code_element = page.locator('#captcha-code')
            captcha_input_element = page.locator('#captchaInput')

            # Get the captcha text. Playwright's text_content() is robust.
            captcha_text = captcha_code_element.text_content()
            if not captcha_text:
                print("Could not retrieve captcha text. Exiting.")
                return None

            print(f"Filling form with Case Type: {case_type}, Number: {case_number}, Year: {year}, Captcha: {captcha_text}")

            # Fill the input fields
            case_type_element.select_option(label=case_type)
            case_number_element.fill(case_number)
            case_year_element.select_option(year)
            captcha_input_element.fill(captcha_text)

            # Click the submit button
            print("Clicking submit button...")
            submit_button_element.click()

            # Wait for navigation or specific element to appear after submission
            # Using page.wait_for_load_state('networkidle') is often more reliable
            # than a fixed sleep, as it waits until network activity is minimal.
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
    result_url=soup.find('a', href=lambda href: href and href.startswith("https://delhihighcourt.nic.in/app/case-type-status-details/"))
    if result_url:
        return result_url.get('href')

Html=submit_case_search('BAIL APPLN.', '1201','2025')
print(extract_url(Html))


"""with open('web1.txt','w') as file:
    file.write(Html)
    print("File 'my_new_file.txt' created successfully.")
"""
"""if __name__ == "__main__":
    case_type = 'BAIL APPLN.'
    case_number = '2198'
    year ='2025'
"""