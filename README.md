Delhi High Court Case Search Portal

This project is a web application that automates the process of searching for a case on the Delhi High Court website, extracts key details and related orders, and generates a downloadable PDF report. The application uses a Flask backend to handle user requests, scrape the data, and create the reports, while a simple HTML frontend provides a user-friendly interface.
✨ Features

    Case Search: Search for a specific case using its type, number, and year.

    Automated Scraping: Uses Playwright to navigate the Delhi High Court website and submit search queries.

    Data Extraction: Parses the HTML response using BeautifulSoup to extract key case details and links to official orders.

    PDF Generation: Compiles the extracted information into a professional, downloadable PDF report using FPDF.

    Web Interface: A responsive and easy-to-use frontend for inputting search criteria and viewing results.

🛠️ Technologies Used

    Backend: Python (with Flask)

    Web Scraping: Playwright, BeautifulSoup

    PDF Generation: FPDF

    Frontend: HTML, CSS, JavaScript (for asynchronous requests)

📋 Prerequisites

Before you begin, ensure you have the following installed:

    Python 3.x

    pip (Python package installer)

    Node.js (Playwright requires a Node.js environment to install browser binaries)

🚀 Installation and Setup

    Clone the repository:

    git clone [your-repository-url]
    cd [your-repository-name]

    Install Python dependencies:

    pip install -r requirements.txt

    If you don't have a requirements.txt file, you can create one by running:

    pip install Flask beautifulsoup4 fpdf playwright

    Install Playwright browser binaries:
    Playwright needs to download the browsers it controls. Run this command to install the necessary binaries:

    playwright install

    File Structure:
    Make sure your project structure looks like this:

    /your-project-directory
    ├── app.py
    ├── extractor.py
    ├── templates/
    │   └── app.html
    ├── requirements.txt
    └── README.md

▶️ Usage

    Run the Flask application:

    python app.py

    The application will start, and you will see a message in your terminal indicating the server is running.

    Open the web browser:
    Navigate to http://127.0.0.1:8080 (or http://localhost:8080) in your web browser.

    Perform a search:

        Fill out the form with a Case Type, Case Number, and Year.

        Click the "Search" button.

        The results will be displayed on the page, and a link to download the PDF report will appear.
