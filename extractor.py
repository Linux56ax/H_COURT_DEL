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
    

#Get Filing Date
def get_filing_date(case_type: str, case_number: str, year: str):
    court_url = "https://dhcmisc.nic.in/pcase/guiCaseWise.php"

    with sync_playwright() as p:
        # Launch headless Chromium
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Go to the court URL
            page.goto(court_url, timeout=60000)

            # Fill form fields
            page.select_option('#ctype', case_type)
            page.fill('#regno', case_number)
            page.select_option('#regyr', year)

            # Get captcha text directly from the element
            captcha_text = page.inner_text('#cap').strip()
            page.fill('input[name="captcha_code"]', captcha_text)

            # Click submit button
            page.click('input[name="Submit"]')

            print("Waiting for results to load...")
            time.sleep(5)  # can be replaced with proper wait

            # Get page content for BeautifulSoup
            page_html = page.content()

        except Exception as e:
            print(f"An error occurred: {e}")
            browser.close()
            return None

        browser.close()

    # Parse filing date with BeautifulSoup
    try:
        html = BeautifulSoup(page_html, 'html.parser')
        target_elements = html.find(id="form3")
        data = target_elements.find('table')
        filing_date = data.find('tbody').find('tr').find_all('td')[-1].text.strip().split("-")

        date_map = {
            'jan': '01',
            'feb': '02',
            'mar': '03',
            'apr': '04',
            'may': '05',
            'jun': '06',
            'jul': '07',
            'aug': '08',
            'sep': '09',
            'oct': '10',
            'nov': '11',
            'dec': '12'
        }

        try:
            filing_date[1] = date_map[filing_date[1].strip().lower()]
        except KeyError:
            print("Invalid month in date")

        return f"{filing_date[2]}/{filing_date[1]}/{filing_date[0]}"

    except Exception as e:
        print(f"An error occurred while parsing the filing date: {e}")
        return None


# Function to extract case details and generate PDF
def order_extractor(user_case_type, user_case_number, user_case_year):
    data={
        "case_type": user_case_type,
        "case_number": user_case_number,
        "case_year": user_case_year

    }
    
    result_html = extract_details(submit_case_search(user_case_type, user_case_number, user_case_year))
    if result_html:
        print("Next step: Parse the returned HTML.")
        data['Petitioner']= result_html[1]
        data['Respondent']= result_html[2]
        data['Last Date']= result_html[3]
        data['Court No']= result_html[4]
        data_n={}
        order=(submit_order_search(result_html[0]))
        if order:
            pdf_data=extract_url(order, data)
            data_n=pdf_data 
    data_n['Filing Date']=get_filing_date(user_case_type, user_case_number, user_case_year)
    return data 

def get_pdf_filename(data):
    """Helper function to create a filename based on case data."""
    case_type = data.get('case_type', 'case')
    case_number = data.get('case_number', '0000')
    case_year = data.get('case_year', '0000')
    return f"{case_type}_{case_number}_{case_year}_details.pdf"

def pdf_generator(pdf_data, save_to_disk=True):
    """
    Generates a PDF document from case data.
    
    Args:
        pdf_data (dict): A dictionary containing case information.
        save_to_disk (bool): If True, saves the PDF to a temporary file.
                             If False, returns the PDF as a string.
    
    Returns:
        str: The file path if saved to disk, or the PDF content as a string.
    """
    if not pdf_data:
        print("No data available to generate PDF.")
        return None

    # Strip prefix from last date string
    last_date = pdf_data.get('Last Date', 'N/A')
    if isinstance(last_date, str) and last_date.startswith('Last Date: '):
        last_date = last_date.replace('Last Date: ', '')

    # Initialize PDF object
    pdf = FPDF()
    pdf.add_page()

    # ======= HEADER =======
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 12, 'DELHI HIGH COURT', ln=True, align='C')
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f"{pdf_data['case_type']} {pdf_data['case_number']}/{pdf_data['case_year']}", ln=True, align='C')
    pdf.ln(10)

    # ======= CASE INFORMATION =======
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'CASE INFORMATION', ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font('Arial', '', 10)
    case_info = [
        ("Case Type:", pdf_data.get('case_type', 'N/A')),
        ("Case Number:", pdf_data.get('case_number', 'N/A')),
        ("Year:", pdf_data.get('case_year', 'N/A')),
        ("Filing Date:", pdf_data.get('Filing Date', 'N/A')),
        ("Last Date:", last_date),
        ("Court No:", pdf_data.get('Court No', 'N/A')),
    ]

    for label, value in case_info:
        pdf.cell(50, 6, label)
        pdf.cell(0, 6, str(value), ln=True)

    pdf.ln(8)

    # ======= PARTIES =======
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'PARTIES', ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font('Arial', '', 10)
    pdf.cell(50, 6, 'Petitioner:')
    pdf.multi_cell(0, 6, pdf_data.get('Petitioner', 'N/A'))
    pdf.ln(2)

    pdf.cell(50, 6, 'Respondent:')
    pdf.multi_cell(0, 6, pdf_data.get('Respondent', 'N/A'))
    pdf.ln(8)

    # ======= ORDERS & DOCUMENTS =======
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'ORDERS & DOCUMENTS', ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font('Arial', '', 10)
    
    # Get the lists of links and dates from the nested dictionary
    orders_data = pdf_data.get('orders', {})
    links = orders_data.get('link', [])
    dates = orders_data.get('order_dates', [])
    
    # Check if we have orders and that the lists have the same length
    if links and dates and len(links) == len(dates):
        for idx, (order_date, link) in enumerate(zip(dates, links), 1):
            # Order number and date
            pdf.cell(15, 6, f"{idx}.")
            pdf.cell(30, 6, "Date:")
            pdf.cell(40, 6, order_date)

            # Clickable link
            link_text = "Click to view document"
            pdf.set_text_color(0, 0, 255)
            pdf.set_font('Arial', 'U', 10)
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
        temp_dir = os.path.join(tempfile.gettempdir(), 'court_case_pdfs')
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, get_pdf_filename(pdf_data))
        pdf.output(file_path)
        print(f"PDF saved to: {file_path}")
        return file_path
    else:
        return pdf.output(dest='S').encode('latin1')



if __name__ == "__main__":
    case_type = "W.P.(C)"
    case_number = "4352"
    year = "2025"
    pdf_data=(order_extractor(case_type, case_number, year))
    pdf_file = pdf_generator(pdf_data)
    
    if pdf_file:
        print(f"PDF generated successfully: {pdf_file}")