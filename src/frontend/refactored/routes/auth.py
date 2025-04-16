"""
Authentication routes for the SustainaTrend™ Intelligence Platform.

This module contains the routes for user authentication, including login, logout,
registration, and password reset.
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, session
import logging
from datetime import datetime, timedelta
import json
import bcrypt
import jwt
import os

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Mock user database for demonstration
users = {
    'admin@sustainatrend.com': {
        'id': 1,
        'username': 'admin',
        'password': bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()),
        'role': 'admin',
        'created_at': datetime.now().isoformat()
    }
}

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'GET':
        return render_template('auth/login.html', title='Login')
    
    try:
        data = request.form
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return redirect(url_for('auth.login'))
        
        user = users.get(email)
        if not user:
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Create session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['logged_in'] = True
            
            flash('Login successful', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        flash('An error occurred during login', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'GET':
        return render_template('auth/register.html', title='Register')
    
    try:
        data = request.form
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not email or not username or not password or not confirm_password:
            flash('All fields are required', 'error')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))
        
        if email in users:
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users[email] = {
            'id': len(users) + 1,
            'username': username,
            'password': hashed_password,
            'role': 'user',
            'created_at': datetime.now().isoformat()
        }
        
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        flash('An error occurred during registration', 'error')
        return redirect(url_for('auth.register'))

@auth_bp.route('/logout')
def logout():
    """Handle user logout."""
    try:
        session.clear()
        flash('You have been logged out', 'success')
        return redirect(url_for('main.index'))
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        flash('An error occurred during logout', 'error')
        return redirect(url_for('main.index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset request."""
    if request.method == 'GET':
        return render_template('auth/forgot_password.html', title='Forgot Password')
    
    try:
        email = request.form.get('email')
        if not email:
            flash('Email is required', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        if email not in users:
            flash('Email not found', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        # In a real application, this would send a password reset email
        flash('Password reset instructions have been sent to your email', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        logger.error(f"Error during password reset request: {str(e)}")
        flash('An error occurred during password reset request', 'error')
        return redirect(url_for('auth.forgot_password'))

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset."""
    if request.method == 'GET':
        return render_template('auth/reset_password.html', title='Reset Password', token=token)
    
    try:
        # In a real application, this would verify the token
        data = request.form
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not password or not confirm_password:
            flash('All fields are required', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        
        # In a real application, this would update the user's password
        flash('Password has been reset successfully', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        logger.error(f"Error during password reset: {str(e)}")
        flash('An error occurred during password reset', 'error')
        return redirect(url_for('auth.login')) 