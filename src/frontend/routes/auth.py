from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import logging
import bcrypt
from datetime import datetime, timedelta
import jwt
import os

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

# In a real application, you would use a database to store users
# For demo purposes, we'll use a simple dictionary
USERS = {
    "admin@trendsense.com": {
        "id": "1",
        "name": "Admin User",
        "password": bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()),
        "role": "admin"
    },
    "vc@trendsense.com": {
        "id": "2",
        "name": "VC User",
        "password": bcrypt.hashpw("vc123".encode('utf-8'), bcrypt.gensalt()),
        "role": "vc"
    }
}

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password', 'error')
            return render_template('auth/login.html')
        
        user = USERS.get(email)
        if not user:
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html')
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Create a session for the user
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            session['logged_in'] = True
            
            # Generate a JWT token
            token = jwt.encode(
                {
                    'user_id': user['id'],
                    'exp': datetime.utcnow() + timedelta(days=1)
                },
                os.getenv('SECRET_KEY', 'dev-key-change-in-production'),
                algorithm='HS256'
            )
            
            session['token'] = token
            
            # Redirect based on user role
            if user['role'] == 'vc':
                return redirect(url_for('vc_dashboard.vc_dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not name or not email or not password or not confirm_password:
            flash('Please fill in all fields', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        if email in USERS:
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        
        # In a real application, you would save the user to a database
        # For demo purposes, we'll just add it to our dictionary
        USERS[email] = {
            "id": str(len(USERS) + 1),
            "name": name,
            "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()),
            "role": "user"
        }
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """
    Handle user logout.
    """
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/api/auth/check', methods=['GET'])
def check_auth():
    """
    Check if the user is authenticated.
    """
    if 'user_id' in session and session.get('logged_in'):
        return jsonify({
            "authenticated": True,
            "user": {
                "id": session.get('user_id'),
                "name": session.get('user_name'),
                "role": session.get('user_role')
            }
        })
    return jsonify({"authenticated": False}), 401 