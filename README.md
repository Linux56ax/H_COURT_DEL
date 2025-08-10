# Delhi High Court Case Search Portal

This project is a web application that automates the process of searching for a case on the Delhi High Court website, extracts key details and related orders, and generates a downloadable PDF report. The application uses a Flask backend to handle user requests, scrape the data, and create the reports, while a simple HTML frontend provides a user-friendly interface.

**Note:** The current version of `extractor.py` uses mock data for demonstration purposes and does not perform live web scraping.

## ✨ Features

*   **Case Search**: Search for a specific case using its type, number, and year.
*   **Data Extraction**: Parses HTML to extract key case details and links to official orders.
*   **PDF Generation**: Compiles the extracted information into a downloadable PDF report.
*   **Web Interface**: A responsive and easy-to-use frontend for inputting search criteria and viewing results.

## 🛠️ Technologies Used

*   **Backend**: Python (with Flask)
*   **Web Scraping**: BeautifulSoup (Playwright is set up for future implementation)
*   **PDF Generation**: FPDF
*   **Frontend**: HTML, CSS, JavaScript

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
*   Python 3.x
*   `pip` (Python package installer)

## 🚀 Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd H_COURT_DEL
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install Flask beautifulsoup4 fpdf playwright
    ```

4.  **Install Playwright browser binaries:**
    (This is required for the intended web scraping functionality)
    ```bash
    playwright install
    ```

## 📂 Project Structure

```
/H_COURT_DEL
├── app.py              # Main Flask application
├── extractor.py        # Data extraction and PDF generation logic
├── templates/
│   └── app.html        # Frontend HTML, CSS, and JavaScript
├── .gitignore
├── LICENSE
└── README.md
```

## ▶️ Usage

1.  **Run the Flask application:**
    ```bash
    python app.py
    ```
    The server will start on `http://127.0.0.1:8080`.

2.  **Open the web browser:**
    Navigate to `http://127.0.0.1:8080` in your web browser.

3.  **Perform a search:**
    *   Fill out the form with a Case Type, Case Number, and Year.
    *   Click the "Search" button.
    *   The results will be displayed on the page, and a link to download the PDF report will appear.

## 📝 Important Note on `extractor.py`

The `submit_case_search` function in `extractor.py` is currently a mock. It returns hardcoded HTML and does not perform a live search on the Delhi High Court website. To implement live web scraping, you will need to replace the mock function with your own Playwright logic.