import os
import tempfile
from flask import Flask, render_template, request, jsonify, send_from_directory
from extractor import submit_case_search, extract_details, extract_url, generate_pdf

# Initialize the Flask application
app = Flask(__name__)

# A dictionary to store generated PDF files in a temporary location.
pdf_temp_dir = os.path.join(tempfile.gettempdir(), 'case_search_pdfs')
os.makedirs(pdf_temp_dir, exist_ok=True)

# Define the route for the home page ("/")
@app.route("/")
def base():
    """
    This function is executed when a user navigates to the root URL.
    It renders the 'app.html' template located in the 'templates' directory.
    """
    return render_template('app.html')

@app.route("/search", methods=['POST'])
def search():
    """
    This route handles the POST request from the frontend form.
    It takes the form data, calls the scraping functions, generates a PDF,
    and returns a JSON response with details and a download URL.
    """
    data = request.json
    case_type = data.get('caseType')
    case_number = data.get('caseNumber')
    year = data.get('year')

    if not all([case_type, case_number, year]):
        return jsonify({'error': 'Missing form data'}), 400

    print(f"Received search request for: {case_type}, {case_number}, {year}")
    
    try:
        # Step 1: Simulate the initial search to get HTML
        search_html = submit_case_search(case_type, case_number, year)
        if not search_html:
            return jsonify({'error': 'No results found.'}), 404

        # Step 2: Extract case details and individual order links
        case_details = extract_details(search_html)
        order_links = extract_url(search_html)
        
        # Create a list of order dictionaries with mock dates
        orders_details = []
        for i, link in enumerate(order_links):
            orders_details.append({
                'date': f'0{i+1}-08-2025',  # Mock date
                'link': link
            })
        
        # Step 3: Generate a PDF report with all the data
        pdf_file_path = generate_pdf(case_details, orders_details)
        filename = os.path.basename(pdf_file_path)

        # Step 4: Return the extracted data and the PDF download URL to the frontend
        response_data = {
            'case_details': case_details,
            'orders_details': orders_details,
            'download_url': f'/download/{filename}'
        }
        return jsonify(response_data), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """
    This route serves the generated PDF file for download.
    """
    try:
        return send_from_directory(pdf_temp_dir, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

# This block ensures the server runs only when the script is executed directly,
# not when it's imported as a module.
if __name__ == "__main__":
    port = 8080
    debug = True
    host = '0.0.0.0'
    print(f"Starting server on {host}:{port} (debug={debug})")
    app.run(debug=debug, port=port, host=host)
