# The extractor.py file is assumed to contain the full code as provided in the analysis
# with the addition of a `generate_pdf` function.
from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup
import time
from fpdf import FPDF
import os 
import tempfile

#Case URL for order search
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


#Function to extract the Case deatils and URL file for orderds
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
    # print(petitioner_name, respondent_name, last_date, court_no)
    
    # Print the extracted information

    result_url=soup.find('a', href=lambda href: href and href.startswith("https://delhihighcourt.nic.in/app/case-type-status-details/"))
    if result_url:
        return result_url.get('href'),petitioner_name, respondent_name, last_date, court_no
    

# Function to submit order search and extract URLs
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
def extract_url(result:str, data:dict):
    soup = BeautifulSoup(result, 'html.parser')
    all_text_content = soup.stripped_strings
    dates=[]
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
                dates.append(word)
    result_url=soup.find_all('a', href=lambda href: href and href.startswith("https://delhihighcourt.nic.in/app/showlogo/"))
    order = {}
    urls = []
    j=1
    for _ in result_url:
        urls.append(_.get('href'))
    order['link']=urls
    order['order_dates']=dates
    data['orders']=order
    if result_url:
        return data


# Function to generate PDF from extracted data
def generate_pdf(data: dict, save_to_disk: bool = False):
    """
    Generates a PDF report from the extracted case data.

    Args:
        data (dict): A dictionary containing all the case details and orders.
        save_to_disk (bool): If True, saves the PDF to a temporary file and returns the path.
                            If False, returns the PDF as a byte string.

    Returns:
        str or bytes: The file path if saved to disk, or the PDF bytes.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    
    # ======= HEADER =======
    pdf.cell(0, 10, 'Delhi High Court Case Report', ln=True, align='C')
    pdf.ln(5)

    # ======= CASE DETAILS =======
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Case Details', ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(40, 6, 'Case Type:', 0)
    pdf.cell(0, 6, data.get('case_type', 'N/A'), ln=True)
    pdf.cell(40, 6, 'Case Number:', 0)
    pdf.cell(0, 6, data.get('case_number', 'N/A'), ln=True)
    pdf.cell(40, 6, 'Year:', 0)
    pdf.cell(0, 6, data.get('year', 'N/A'), ln=True)
    pdf.cell(40, 6, 'Petitioner:', 0)
    pdf.multi_cell(0, 6, data.get('petitioner', 'N/A'))
    pdf.cell(40, 6, 'Respondent:', 0)
    pdf.multi_cell(0, 6, data.get('respondent', 'N/A'))
    pdf.cell(40, 6, 'Last Date:', 0)
    pdf.cell(0, 6, data.get('last_date', 'N/A'), ln=True)
    pdf.cell(40, 6, 'Court No.:', 0)
    pdf.cell(0, 6, data.get('court_no', 'N/A'), ln=True)

    # ======= ORDERS SECTION =======
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Orders', ln=True)
    pdf.set_font('Arial', '', 10)

    orders = data.get('orders', {})
    order_links = orders.get('link', [])
    order_dates = orders.get('order_dates', [])

    if order_links:
        for i, link in enumerate(order_links):
            pdf.set_text_color(0, 0, 255) # Blue for links
            pdf.set_font('Arial', 'U', 10) # Underline
            
            link_text = f"Order {i+1} - Date: {order_dates[i] if i < len(order_dates) else 'N/A'}"
            pdf.cell(0, 6, link_text, ln=True, link=link)

            # Reset styling
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 10)

            # Show URL preview
            pdf.set_font('Arial', '', 8)
            pdf.set_text_color(100, 100, 100)
            url_display = link[:80] + ('...' if len(link) > 80 else '')
            pdf.cell(65, 4, "")
            pdf.cell(0, 4, f"URL: {url_display}", ln=True)

            # Reset
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 10)
            pdf.ln(3)
    else:
        pdf.cell(0, 6, 'No orders available', ln=True)

    # ======= FOOTER =======
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 6, f'Generated on: {time.strftime("%Y-%m-%d %H:%M:%S")}', ln=True, align='C')

    # ======= SAVE OR RETURN =======
    if save_to_disk:
        temp_dir = os.path.join(tempfile.gettempdir(), 'case_search_pdfs')
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, f'case_report_{data.get("case_number")}_{time.time()}.pdf')
        pdf.output(file_path, 'F')
        return file_path
    else:
        return pdf.output(dest='S').encode('latin1')
