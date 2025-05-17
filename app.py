import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify
from database import get_pending_orders, test_connection
from config import load_config

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "microsip_dashboard_secret")

# Load the configuration
config = load_config()

@app.route('/')
def index():
    """Render the main dashboard page."""
    try:
        # Test the database connection
        test_connection()
        # Get initial data
        orders = get_pending_orders()
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return render_template('index.html', orders=orders, last_updated=last_updated, config=config)
    except Exception as e:
        logging.error(f"Error loading dashboard: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/api/orders')
def api_orders():
    """API endpoint to get the latest orders data."""
    try:
        orders = get_pending_orders()
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return jsonify({
            'success': True,
            'orders': orders,
            'last_updated': last_updated
        })
    except Exception as e:
        logging.error(f"Error fetching orders: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Página no encontrada"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Error interno del servidor"), 500

# Custom filter to format dates
@app.template_filter('formatdate')
def format_date(value, format="%d/%m/%Y"):
    """Format a date according to the given format."""
    if value:
        if isinstance(value, datetime) or hasattr(value, 'strftime'):
            return value.strftime(format)
        return value
    return ""
