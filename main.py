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
def extract_details(result:str):
    soup = BeautifulSoup(result, 'html.parser')
    #print(soup)
    # Find the specific row (<tr>) that contains the data
    # We can identify it by looking for the <td> with class 'sorting_1' which contains '1'
    data_row = soup.find('td', class_='sorting_1').parent

    # Extract the second <td> which contains the Petitioner vs. Respondent information
    petitioner_respondent_td = data_row.find_all('td')[2]
    # Get all the text within this <td>, splitting by the <br/> tags
    petitioner_respondent_text_list = petitioner_respondent_td.stripped_strings
    petitioner_respondent_list = [text.strip() for text in petitioner_respondent_text_list if text.strip()]

    # Extract the third <td> which contains the date and court number
    date_court_td = data_row.find_all('td')[3]
    # Get all the text within this <td>, splitting by the <br/> tags
    date_court_text_list = date_court_td.stripped_strings
    date_court_list = [text.strip() for text in date_court_text_list if text.strip()]

    # Clean and assign the extracted values
    petitioner_name = petitioner_respondent_list[0]
    respondent_name = petitioner_respondent_list[2]
    last_date = date_court_list[1].strip()
    court_no = date_court_list[2].strip()
    
    # Print the extracted information

    result_url=soup.find('a', href=lambda href: href and href.startswith("https://delhihighcourt.nic.in/app/case-type-status-details/"))
    if result_url:
        return result_url.get('href'),petitioner_name, respondent_name, last_date, court_no

Html=submit_case_search('BAIL APPLN.', '1201','2025')

z=[extract_details(Html)]
print(z)


"""with open('web1.txt','w') as file:
    file.write(Html)
    print("File 'my_new_file.txt' created successfully.")
"""
"""if __name__ == "__main__":
    case_type = 'BAIL APPLN.'
    case_number = '2198'
    year ='2025'
"""