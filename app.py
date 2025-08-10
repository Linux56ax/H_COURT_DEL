# from flask import Flask, render_template

# # Initialize the Flask application
# # The __name__ argument helps Flask locate resources like templates and static files.
# app = Flask(__name__)

# # Define the route for the home page ("/")
# @app.route("/")
# def base():
#     """
#     This function is executed when a user navigates to the root URL.
#     It renders the 'app.html' template located in the 'templates' directory.
#     """
#     return render_template('app.html')

# # This block ensures the server runs only when the script is executed directly,
# # not when it's imported as a module.
# if __name__ == "__main__":
#     # Server configuration
#     port = 8080
#     debug = True  # Enable debug mode for automatic reloading on code changes
#     host =  '0.0.0.0' # Listen on all public IPs

#     print(f"Starting server on {host}:{port} (debug={debug})")
    
#     # Run the Flask development server
#     app.run(debug=debug, port=port, host=host)











import os
import tempfile
from flask import Flask, render_template, request, jsonify, send_from_directory
from extractor import submit_case_search, extract_details, submit_order_search, extract_url, generate_pdf

# Initialize the Flask application
# The __name__ argument helps Flask locate resources like templates and static files.
app = Flask(__name__)

# A dictionary to store generated PDF files in a temporary location.
# This is a simple in-memory storage for demonstration.
# In a production environment, you would use a proper file storage system.
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
    It takes the form data, calls the scraping functions, and returns a JSON response.
    """
    data = request.json
    case_type = data.get('caseType')
    case_number = data.get('caseNumber')
    year = data.get('year')

    if not all([case_type, case_number, year]):
        return jsonify({'error': 'Missing form data'}), 400

    print(f"Received search request for: {case_type}, {case_number}, {year}")

    try:
        # Step 1: Submit the initial case search and get the result page HTML.
        case_search_html = submit_case_search(case_type, case_number, year)
        if not case_search_html:
            return jsonify({'error': 'Could not perform initial case search.'}), 500

        # Step 2: Extract the details and the URL for the orders page.
        orders_url, petitioner, respondent, last_date, court_no = extract_details(case_search_html)
        
        case_data = {
            'petitioner': petitioner,
            'respondent': respondent,
            'last_date': last_date,
            'court_no': court_no,
            'case_type': case_type,
            'case_number': case_number,
            'year': year
        }

        # Step 3: Use the orders_url to get the orders page HTML.
        orders_html = submit_order_search(orders_url)
        if not orders_html:
            return jsonify({'error': 'Could not retrieve orders page.'}), 500

        # Step 4: Extract the URLs of the individual orders.
        final_data = extract_url(orders_html, case_data)

        # Step 5: Generate a PDF report with all the data.
        pdf_file_path = generate_pdf(final_data, save_to_disk=True)
        filename = os.path.basename(pdf_file_path)

        # Return the extracted data and the PDF download URL to the frontend.
        response_data = {
            'case_details': {
                'petitioner': petitioner,
                'respondent': respondent,
                'last_date': last_date,
                'court_no': court_no,
                'orders_count': len(final_data.get('orders', {}).get('link', []))
            },
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
    return send_from_directory(pdf_temp_dir, filename, as_attachment=True)


# This block ensures the server runs only when the script is executed directly,
# not when it's imported as a module.
if __name__ == "__main__":
    # Server configuration
    port = 8080
    debug = True  # Enable debug mode for automatic reloading on code changes
    host = '0.0.0.0' # Listen on all public IPs

    print(f"Starting server on {host}:{port} (debug={debug})")
    
    # Run the Flask development server
    app.run(debug=debug, port=port, host=host)

