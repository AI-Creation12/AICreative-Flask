from flask import Flask
from flask_cors import CORS
from .routes import setup_routes

# Initialize the Flask application
app = Flask(__name__)

# Enable CORS option 
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
# Setup all routes from the routes module
setup_routes(app)