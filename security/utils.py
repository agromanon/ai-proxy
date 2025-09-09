"""
Authentication utilities and decorators
"""

from functools import wraps
from flask import request, redirect, url_for, session, jsonify
import hashlib
import secrets

def require_auth(f):
    """
    Decorator to require user authentication
    Checks both session and API key authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check session authentication
        if 'user_id' in session:
            return f(*args, **kwargs)
        
        # Check API key authentication
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            # In a full implementation, we would validate the API key here
            # For now, we'll just check if it exists
            api_key = auth_header[7:]  # Remove 'Bearer ' prefix
            if api_key:
                # Add user info to request context
                request.user = {'id': 1, 'username': 'api_user', 'is_admin': False}
                return f(*args, **kwargs)
        
        # Return 401 for API requests, redirect for web requests
        if request.is_json or request.headers.get('Accept', '').startswith('application/json'):
            return jsonify({'error': 'Authentication required'}), 401
        else:
            return redirect(url_for('login', next=request.url))
    
    return decorated_function

def require_admin(f):
    """
    Decorator to require admin privileges
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check session authentication
        if 'user_id' in session and session.get('is_admin'):
            return f(*args, **kwargs)
        
        # Check API key authentication
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            # In a full implementation, we would validate the API key here
            # For now, we'll just check if it's an admin
            api_key = auth_header[7:]  # Remove 'Bearer ' prefix
            if api_key and api_key == 'admin-key':  # Simplified check
                # Add user info to request context
                request.user = {'id': 1, 'username': 'admin', 'is_admin': True}
                return f(*args, **kwargs)
        
        # Return 403 for API requests, redirect for web requests
        if request.is_json or request.headers.get('Accept', '').startswith('application/json'):
            return jsonify({'error': 'Admin privileges required'}), 403
        else:
            return redirect(url_for('login'))
    
    return decorated_function

def get_current_user():
    """
    Get current user from session or API key
    
    Returns:
        User info dict or None
    """
    # Check session
    if 'user_id' in session:
        return {
            'id': session['user_id'],
            'username': session.get('username'),
            'is_admin': session.get('is_admin', False)
        }
    
    # Check API key
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        api_key = auth_header[7:]  # Remove 'Bearer ' prefix
        # In a full implementation, we would validate the API key here
        if api_key:
            return {'id': 1, 'username': 'api_user', 'is_admin': False}
    
    return None

def generate_secure_token():
    """Generate a cryptographically secure token"""
    return secrets.token_urlsafe(32)

def sanitize_input(input_string: str) -> str:
    """
    Sanitize user input to prevent XSS
    
    Args:
        input_string: Input string to sanitize
        
    Returns:
        Sanitized string
    """
    import html
    return html.escape(input_string)

# Flask session configuration helper
def configure_session(app):
    """
    Configure Flask session settings
    
    Args:
        app: Flask application instance
    """
    # Get app settings (in a full implementation, we would get these from the database)
    # For now, we'll use default values
    app.config.update(
        SECRET_KEY='dev-secret-key',  # In production, this should come from config
        SESSION_COOKIE_SECURE=False,  # In production, set to True with HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax'
    )