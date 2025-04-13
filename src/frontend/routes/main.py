from flask import Blueprint, render_template, redirect, url_for
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Render the main landing page or redirect to the dashboard.
    """
    try:
        # In a real application, you would check if the user is authenticated
        # and redirect accordingly. For demo purposes, we'll redirect to the VC dashboard.
        return redirect(url_for('vc_dashboard.vc_dashboard'))
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return render_template('error.html', message="An error occurred while loading the page"), 500

@main_bp.route('/about')
def about():
    """
    Render the about page.
    """
    try:
        return render_template('about.html')
    except Exception as e:
        logger.error(f"Error rendering about page: {str(e)}")
        return render_template('error.html', message="An error occurred while loading the page"), 500

@main_bp.route('/contact')
def contact():
    """
    Render the contact page.
    """
    try:
        return render_template('contact.html')
    except Exception as e:
        logger.error(f"Error rendering contact page: {str(e)}")
        return render_template('error.html', message="An error occurred while loading the page"), 500 