import os
import tempfile
import time
from fpdf import FPDF
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Page

# Mock functions to simulate data extraction
def submit_case_search(case_type: str, case_number: str, year: str) -> str | None:
    """
    Simulates submitting a case search and returning HTML content.
    This mock has been updated to include three order links.
    """
    print(f"Simulating search for Case: {case_type} - {case_number} of {year}")
    # The mock HTML is updated to reflect three order links.
    return """
    <html><body>
        <div id="case-details">
            <p>Petitioner: M.R. Sharma vs. The State of Delhi</p>
            <p>Last Date: 05-08-2025</p>
            <p>Court No: Court No. 13</p>
        </div>
        <div id='order-links-section'>
            <a href='https://example.com/order1.pdf'>Order 1</a>
            <a href='https://example.com/order2.pdf'>Order 2</a>
            <a href='https://example.com/order3.pdf'>Order 3</a>
        </div>
    </body></html>
    """

def extract_details(html_content: str) -> dict:
    """
    Extracts case details from HTML, specifically splitting the petitioner and
    respondent names based on the 'vs.' string.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the element with the petitioner's name and split it
    petitioner_line = soup.find(text=lambda text: 'Petitioner' in text).split(':')[-1].strip()
    
    # Split the name based on " vs. "
    if " vs. " in petitioner_line:
        petitioner_name, respondent_name = petitioner_line.split(" vs. ", 1)
    else:
        # Fallback if "vs." is not found
        petitioner_name = petitioner_line
        respondent_name = "N/A"

    last_date = soup.find(text=lambda text: 'Last Date' in text).split(':')[-1].strip()
    court_no = soup.find(text=lambda text: 'Court No' in text).split(':')[-1].strip()

    return {
        'petitioner': petitioner_name,
        'respondent': respondent_name,
        'last_date': last_date,
        'court_no': court_no
    }


def extract_url(html_content: str) -> list[str]:
    """
    Extracts all order URLs from the HTML content within the designated section.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    # Use select with a more specific CSS selector to find all a tags
    links = [a['href'] for a in soup.select('#order-links-section a')]
    print(f"Extracted URLs: {links}")
    return links

def generate_pdf(case_details: dict, order_links: list[dict], save_to_disk=True) -> str:
    """
    Generates a PDF report with case details and order links.
    Returns the path to the saved PDF file.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Court Case Report', 0, 1, 'C')
    pdf.ln(10)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Case Details:', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    # Now using the separated names
    pdf.cell(0, 6, f"Petitioner: {case_details['petitioner']}", 0, 1)
    pdf.cell(0, 6, f"Respondent: {case_details['respondent']}", 0, 1)
    pdf.cell(0, 6, f"Last Date: {case_details['last_date']}", 0, 1)
    pdf.cell(0, 6, f"Court No.: {case_details['court_no']}", 0, 1)
    
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Order Links:', 0, 1)
    pdf.set_font('Arial', 'U', 10)
    pdf.set_text_color(0, 0, 255) # Blue for links
    
    # Iterate through all orders, not just a subset
    for i, order in enumerate(order_links):
        pdf.cell(0, 6, f"Order {i+1} - Date: {order['date']}", 0, 1, link=order['link'])
    
    # ======= FOOTER =======
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f'Generated on: {time.strftime("%Y-%m-%d %H:%M:%S")}', ln=True, align='C')

    # Save to a temporary directory
    pdf_temp_dir = os.path.join(tempfile.gettempdir(), 'case_search_pdfs')
    os.makedirs(pdf_temp_dir, exist_ok=True)
    filename = f"report_{time.time()}.pdf"
    file_path = os.path.join(pdf_temp_dir, filename)
    pdf.output(file_path)
    
    return file_path
