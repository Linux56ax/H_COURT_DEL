from flask import Flask, render_template

# Initialize the Flask application
# The __name__ argument helps Flask locate resources like templates and static files.
app = Flask(__name__)

# Define the route for the home page ("/")
@app.route("/")
def base():
    """
    This function is executed when a user navigates to the root URL.
    It renders the 'app.html' template located in the 'templates' directory.
    """
    return render_template('app.html')

# This block ensures the server runs only when the script is executed directly,
# not when it's imported as a module.
if __name__ == "__main__":
    # Server configuration
    port = 8080
    debug = True  # Enable debug mode for automatic reloading on code changes
    host =  '0.0.0.0' # Listen on all public IPs

    print(f"Starting server on {host}:{port} (debug={debug})")
    
    # Run the Flask development server
    app.run(debug=debug, port=port, host=host)
