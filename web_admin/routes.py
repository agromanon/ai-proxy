"""
Web Admin Routes for AI Proxy
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
import json
import sqlite3
from config.database import db_manager
from config.utils import db_utils
from security.auth_manager import auth_manager, session_manager
from security.utils import require_auth, require_admin, get_current_user
from provider_registry import provider_registry
from dynamic_provider_loader import DynamicProviderLoader

# Create blueprint
web_admin = Blueprint('web_admin', __name__, template_folder='templates', static_folder='static')

# Initialize loader
provider_loader = DynamicProviderLoader(db_manager, provider_registry)

def require_login(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('web_admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@web_admin.route('/')
@require_login
def dashboard():
    """Dashboard/home page"""
    user = get_current_user()
    app_settings = db_utils.get_app_settings()
    prompt_config = db_utils.get_prompt_config()
    providers = provider_loader.load_all_providers()
    
    # Get active provider
    active_provider = None
    for provider in providers:
        if provider['is_active']:
            active_provider = provider
            break
    
    return render_template('dashboard.html', 
                         user=user,
                         app_settings=app_settings,
                         prompt_config=prompt_config,
                         active_provider=active_provider,
                         providers=providers)

@web_admin.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Authenticate user
        user = auth_manager.authenticate_user(username, password)
        if user:
            # Create session
            session_token = session_manager.create_session(
                user['id'], 
                request.remote_addr, 
                request.headers.get('User-Agent')
            )
            
            if session_token:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['is_admin'] = user['is_admin']
                session['session_token'] = session_token
                
                flash('Login successful')
                return redirect(url_for('web_admin.dashboard'))
            else:
                flash('Error creating session')
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@web_admin.route('/logout')
def logout():
    """Logout endpoint"""
    if 'session_token' in session:
        session_manager.destroy_session(session['session_token'])
    
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('web_admin.login'))

@web_admin.route('/providers')
@require_login
def providers_list():
    """List all providers"""
    user = get_current_user()
    providers = provider_loader.load_all_providers()
    provider_info = provider_registry.get_provider_info()
    
    return render_template('providers.html', 
                         user=user,
                         providers=providers,
                         provider_info=provider_info)

@web_admin.route('/provider/new', methods=['GET', 'POST'])
@require_login
def provider_new():
    """Add new provider"""
    user = get_current_user()
    
    if request.method == 'POST':
        # Process form data with simplified model mapping
        provider_data = {
            'name': request.form['name'],
            'api_endpoint': request.form['api_endpoint'],
            'api_key': request.form['api_key'],
            'default_model': request.form.get('default_model', ''),
            'auth_method': request.form.get('auth_method', 'bearer_token'),
            'api_standard': request.form.get('api_standard', 'openai'),
            'is_active': 'is_active' in request.form,
            'headers': {},
            'model_mapping': {}
        }
        
        # Process simplified model mapping
        model_haiku = request.form.get('model_haiku', '').strip()
        model_sonnet = request.form.get('model_sonnet', '').strip()
        model_opus = request.form.get('model_opus', '').strip()
        
        # Build model mapping dictionary
        if model_haiku or model_sonnet or model_opus:
            model_mapping = {}
            if model_haiku:
                model_mapping['haiku'] = model_haiku
                model_mapping['claude-3-haiku-20240307'] = model_haiku
                model_mapping['claude-3-haiku'] = model_haiku
            if model_sonnet:
                model_mapping['sonnet'] = model_sonnet
                model_mapping['claude-3-5-sonnet-20241022'] = model_sonnet
                model_mapping['claude-3-5-sonnet'] = model_sonnet
            if model_opus:
                model_mapping['opus'] = model_opus
                model_mapping['claude-3-opus-20240229'] = model_opus
                model_mapping['claude-3-opus'] = model_opus
            
            provider_data['model_mapping'] = model_mapping
        else:
            # Use JSON model mapping if provided (fallback)
            try:
                json_model_mapping = request.form.get('model_mapping', '{}')
                if json_model_mapping:
                    provider_data['model_mapping'] = json.loads(json_model_mapping)
            except json.JSONDecodeError:
                pass
        
        # Process custom headers
        header_keys = request.form.getlist('header_key[]')
        header_values = request.form.getlist('header_value[]')
        for key, value in zip(header_keys, header_values):
            if key and value:
                provider_data['headers'][key] = value
        
        # Save provider
        try:
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO providers 
                (name, api_endpoint, api_key, default_model, auth_method, api_standard, 
                 supported_models, model_mapping, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                provider_data['name'],
                provider_data['api_endpoint'],
                provider_data['api_key'],
                provider_data['default_model'],
                provider_data['auth_method'],
                provider_data['api_standard'],
                json.dumps({}),  # supported_models (empty for now)
                json.dumps(provider_data['model_mapping']),  # model_mapping as JSON
                provider_data['is_active']
            ))
            
            provider_id = cursor.lastrowid
            
            # Insert headers
            for key, value in provider_data['headers'].items():
                cursor.execute("""
                    INSERT INTO provider_headers 
                    (provider_id, header_key, header_value)
                    VALUES (?, ?, ?)
                """, (provider_id, key, value))
            
            conn.commit()
            flash('Provider added successfully!')
            
        except Exception as e:
            flash(f'Error adding provider: {str(e)}')
        
        return redirect(url_for('web_admin.providers_list'))
    
    # Get available provider types
    provider_types = provider_registry.get_provider_info()
    
    return render_template('provider_form.html', 
                         user=user,
                         provider=None,
                         provider_types=provider_types)

@web_admin.route('/provider/edit/<int:provider_id>', methods=['GET', 'POST'])
@require_login
def provider_edit(provider_id):
    """Edit provider"""
    user = get_current_user()
    
    # Get provider
    provider = provider_loader.get_provider_by_id(provider_id)
    if not provider:
        flash('Provider not found')
        return redirect(url_for('web_admin.providers_list'))
    
    # Parse model mapping for display
    if provider.get('model_mapping'):
        try:
            model_mapping = json.loads(provider['model_mapping'])
            provider['model_mapping'] = model_mapping
            
            # Extract specific models for form fields
            provider['model_mapping']['haiku'] = model_mapping.get('haiku', model_mapping.get('claude-3-haiku-20240307', ''))
            provider['model_mapping']['sonnet'] = model_mapping.get('sonnet', model_mapping.get('claude-3-5-sonnet-20241022', ''))
            provider['model_mapping']['opus'] = model_mapping.get('opus', model_mapping.get('claude-3-opus-20240229', ''))
        except json.JSONDecodeError:
            provider['model_mapping'] = {}
    
    if request.method == 'POST':
        # Process form data with simplified model mapping
        provider_data = {
            'name': request.form['name'],
            'api_endpoint': request.form['api_endpoint'],
            'api_key': request.form['api_key'],
            'default_model': request.form.get('default_model', ''),
            'auth_method': request.form.get('auth_method', 'bearer_token'),
            'api_standard': request.form.get('api_standard', 'openai'),
            'is_active': 'is_active' in request.form,
            'headers': {},
            'model_mapping': {}
        }
        
        # Process simplified model mapping
        model_haiku = request.form.get('model_haiku', '').strip()
        model_sonnet = request.form.get('model_sonnet', '').strip()
        model_opus = request.form.get('model_opus', '').strip()
        
        # Build model mapping dictionary
        if model_haiku or model_sonnet or model_opus:
            model_mapping = {}
            if model_haiku:
                model_mapping['haiku'] = model_haiku
                model_mapping['claude-3-haiku-20240307'] = model_haiku
                model_mapping['claude-3-haiku'] = model_haiku
            if model_sonnet:
                model_mapping['sonnet'] = model_sonnet
                model_mapping['claude-3-5-sonnet-20241022'] = model_sonnet
                model_mapping['claude-3-5-sonnet'] = model_sonnet
            if model_opus:
                model_mapping['opus'] = model_opus
                model_mapping['claude-3-opus-20240229'] = model_opus
                model_mapping['claude-3-opus'] = model_opus
            
            provider_data['model_mapping'] = model_mapping
        else:
            # Use JSON model mapping if provided (fallback)
            try:
                json_model_mapping = request.form.get('model_mapping', '{}')
                if json_model_mapping:
                    provider_data['model_mapping'] = json.loads(json_model_mapping)
            except json.JSONDecodeError:
                pass
        
        # Process custom headers
        header_keys = request.form.getlist('header_key[]')
        header_values = request.form.getlist('header_value[]')
        for key, value in zip(header_keys, header_values):
            if key and value:
                provider_data['headers'][key] = value
        
        # Update provider
        try:
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE providers SET
                name = ?, api_endpoint = ?, api_key = ?, default_model = ?,
                auth_method = ?, api_standard = ?, supported_models = ?, 
                model_mapping = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                provider_data['name'],
                provider_data['api_endpoint'],
                provider_data['api_key'],
                provider_data['default_model'],
                provider_data['auth_method'],
                provider_data['api_standard'],
                json.dumps({}),  # supported_models (empty for now)
                json.dumps(provider_data['model_mapping']),  # model_mapping as JSON
                provider_data['is_active'],
                provider_id
            ))
            
            # Remove existing headers
            cursor.execute("DELETE FROM provider_headers WHERE provider_id = ?", (provider_id,))
            
            # Insert new headers
            for key, value in provider_data['headers'].items():
                cursor.execute("""
                    INSERT INTO provider_headers 
                    (provider_id, header_key, header_value)
                    VALUES (?, ?, ?)
                """, (provider_id, key, value))
            
            conn.commit()
            flash('Provider updated successfully!')
            
        except Exception as e:
            flash(f'Error updating provider: {str(e)}')
        
        return redirect(url_for('web_admin.providers_list'))
    
    # Get available provider types
    provider_types = provider_registry.get_provider_info()
    
    return render_template('provider_form.html', 
                         user=user,
                         provider=provider,
                         provider_types=provider_types)

@web_admin.route('/provider/delete/<int:provider_id>', methods=['POST'])
@require_login
def provider_delete(provider_id):
    """Delete provider"""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        # Delete headers first (due to foreign key constraint)
        cursor.execute("DELETE FROM provider_headers WHERE provider_id = ?", (provider_id,))
        # Delete provider
        cursor.execute("DELETE FROM providers WHERE id = ?", (provider_id,))
        conn.commit()
        
        flash('Provider deleted successfully!')
    except Exception as e:
        flash(f'Error deleting provider: {str(e)}')
    
    return redirect(url_for('web_admin.providers_list'))

@web_admin.route('/provider/activate/<int:provider_id>', methods=['POST'])
@require_login
def provider_activate(provider_id):
    """Activate provider"""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        # First, deactivate all providers
        cursor.execute("UPDATE providers SET is_active = 0")
        # Then, activate the specified provider
        cursor.execute("UPDATE providers SET is_active = 1 WHERE id = ?", (provider_id,))
        conn.commit()
        
        flash('Provider activated successfully!')
    except Exception as e:
        flash(f'Error activating provider: {str(e)}')
    
    return redirect(url_for('web_admin.providers_list'))

@web_admin.route('/provider/test/<int:provider_id>', methods=['POST'])
@require_login
def provider_test(provider_id):
    """Test provider connection"""
    try:
        # Get provider config
        provider_config = provider_loader.get_provider_by_id(provider_id)
        if not provider_config:
            flash('Provider not found')
            return redirect(url_for('web_admin.providers_list'))
        
        # Create provider instance
        provider_instance = provider_loader.create_provider_instance(provider_config)
        if not provider_instance:
            flash('Error creating provider instance')
            return redirect(url_for('web_admin.providers_list'))
        
        # Test connection
        success = provider_instance.test_connection()
        if success:
            flash('Provider connection test successful!')
        else:
            flash('Provider connection test failed!')
            
    except Exception as e:
        flash(f'Error testing provider: {str(e)}')
    
    return redirect(url_for('web_admin.providers_list'))

@web_admin.route('/settings', methods=['GET', 'POST'])
@require_login
def settings():
    """Application settings"""
    user = get_current_user()
    settings_data = db_utils.get_app_settings()
    
    if request.method == 'POST':
        # Process form data
        new_settings = {
            'server_port': int(request.form.get('server_port', 8000)),
            'server_host': request.form.get('server_host', '127.0.0.1'),
            'enable_full_logging': 'enable_full_logging' in request.form,
            'log_directory': request.form.get('log_directory', 'logs'),
            'enable_streaming': 'enable_streaming' in request.form,
            'request_timeout': int(request.form.get('request_timeout', 300)),
            'require_auth': 'require_auth' in request.form,
            'secret_key': request.form.get('secret_key', ''),
            'session_cookie_secure': 'session_cookie_secure' in request.form,
            'rate_limit_enabled': 'rate_limit_enabled' in request.form,
            'rate_limit_requests': int(request.form.get('rate_limit_requests', 100)),
            'rate_limit_window': int(request.form.get('rate_limit_window', 3600))
        }
        
        # Update settings
        success = db_utils.update_app_settings(new_settings)
        if success:
            flash('Settings updated successfully!')
        else:
            flash('Error updating settings')
        
        return redirect(url_for('web_admin.settings'))
    
    return render_template('settings.html', 
                         user=user,
                         settings=settings_data)

@web_admin.route('/prompt-config', methods=['GET', 'POST'])
@require_login
def prompt_config():
    """Prompt configuration"""
    user = get_current_user()
    config_data = db_utils.get_prompt_config()
    
    if request.method == 'POST':
        # Process form data
        new_config = {
            'use_custom_prompt': 'use_custom_prompt' in request.form,
            'prompt_template': request.form.get('prompt_template', ''),
            'system_name': request.form.get('system_name', ''),
            'model_name_override': request.form.get('model_name_override', ''),
            'remove_ai_references': 'remove_ai_references' in request.form,
            'remove_defensive_restrictions': 'remove_defensive_restrictions' in request.form
        }
        
        # Update config
        success = db_utils.update_prompt_config(new_config)
        if success:
            flash('Prompt configuration updated successfully!')
        else:
            flash('Error updating prompt configuration')
        
        return redirect(url_for('web_admin.prompt_config'))
    
    return render_template('prompt_config.html', 
                         user=user,
                         config=config_data)

@web_admin.route('/profile', methods=['GET', 'POST'])
@require_login
def profile():
    """User profile"""
    user = get_current_user()
    
    if request.method == 'POST':
        # Handle password change
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Verify current password
        auth_user = auth_manager.authenticate_user(user['username'], current_password)
        if not auth_user:
            flash('Current password is incorrect')
        elif new_password != confirm_password:
            flash('New passwords do not match')
        elif len(new_password) < 8:
            flash('Password must be at least 8 characters long')
        else:
            # Update password
            success = auth_manager.update_user_password(user['id'], new_password)
            if success:
                flash('Password updated successfully!')
            else:
                flash('Error updating password')
        
        return redirect(url_for('web_admin.profile'))
    
    return render_template('profile.html', user=user)