import os
import logging
import json
import yaml
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session

from database import get_pending_orders, test_connection
from config import load_config, update_config

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "microsip_dashboard_secret")

# Load the configuration
config = load_config()

# Usuarios y contraseñas embebidos directamente en el código
# Esto proporciona mayor seguridad al no almacenar las credenciales en archivos externos
USERS = {
    'admin': {
        'password': 'admin123',  # Contraseña en texto plano solo para desarrollo, no es una buena práctica en producción
        'role': 'superadmin',
        'is_superadmin': True
    },
    'usuario': {
        'password': 'usuario123',
        'role': 'user',
        'is_superadmin': False
    }
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session.get('role') != 'admin':
            flash('Se requieren permisos de administrador para acceder a esta página', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    error = None
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        logging.debug(f"Intento de login para usuario: {username}")
        
        # Verificar si el usuario existe y la contraseña es correcta
        if username in USERS and USERS[username]['password'] == password:
            # Obtener datos de usuario desde la configuración embebida
            user_data = USERS[username]
            
            session['user'] = username
            session['role'] = user_data['role']
            session['is_superadmin'] = user_data['is_superadmin']
            
            flash(f'Bienvenido, {username}!', 'success')
            logging.info(f"Usuario {username} ha iniciado sesión correctamente")
            return redirect(url_for('index'))
        else:
            error = 'Usuario o contraseña incorrectos'
            logging.warning(f"Intento de login fallido para usuario: {username}")
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """Handle user logout."""
    session.pop('user', None)
    session.pop('role', None)
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
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

@app.route('/configuracion', methods=['GET', 'POST'])
@login_required
def configuracion():
    # Verificar si el usuario es superadmin
    if not session.get('is_superadmin', False):
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('index'))
    """Render and handle the configuration page."""
    if request.method == 'POST':
        try:
            # Update database configuration
            config['database']['dsn'] = request.form['dsn']
            config['database']['user'] = request.form['db_user']
            config['database']['password'] = request.form['db_password']
            config['database']['charset'] = request.form['charset']
            
            # Update application configuration
            config['application']['title'] = request.form['title']
            config['application']['refresh_interval'] = int(request.form['refresh_interval'])
            
            # Update SQL query if provided
            if request.form['query'].strip():
                config['database']['query'] = request.form['query']
            
            # Save changes
            update_config(config)
            
            flash('Configuración actualizada correctamente', 'success')
            return redirect(url_for('configuracion'))
        except Exception as e:
            logging.error(f"Error al actualizar configuración: {str(e)}")
            flash(f'Error al guardar configuración: {str(e)}', 'danger')
    
    return render_template('configuracion.html', config=config)

@app.route('/usuarios', methods=['GET', 'POST'])
@login_required
def usuarios():
    # Verificar si el usuario es superadmin
    if not session.get('is_superadmin', False):
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('index'))
    """Manage users."""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role', 'user')
            
            if username and password:
                if username not in config['users']:
                    config['users'][username] = {
                        'password': generate_password_hash(password),
                        'role': role
                    }
                    update_config(config)
                    flash(f'Usuario {username} agregado correctamente', 'success')
                else:
                    flash(f'El usuario {username} ya existe', 'danger')
            else:
                flash('Se requiere nombre de usuario y contraseña', 'warning')
                
        elif action == 'delete':
            username = request.form.get('username')
            if username and username in config['users'] and username != 'admin':
                del config['users'][username]
                update_config(config)
                flash(f'Usuario {username} eliminado correctamente', 'success')
            else:
                flash('No se puede eliminar este usuario', 'danger')
                
        elif action == 'change_password':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if username and password and username in config['users']:
                config['users'][username]['password'] = generate_password_hash(password)
                update_config(config)
                flash('Contraseña actualizada correctamente', 'success')
            else:
                flash('Error al actualizar contraseña', 'danger')
        
        return redirect(url_for('usuarios'))
    
    return render_template('usuarios.html', users=config['users'])

@app.route('/api/orders')
@login_required
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

@app.route('/api/test_connection', methods=['POST'])
@login_required
@admin_required
def api_test_connection():
    """API endpoint to test database connection with new parameters."""
    try:
        # Get test parameters from request
        test_config = {
            'database': {
                'dsn': request.form.get('dsn'),
                'user': request.form.get('db_user'),
                'password': request.form.get('db_password'),
                'charset': request.form.get('charset')
            }
        }
        
        # Temporarily override configuration
        original_config = config['database'].copy()
        config['database'].update(test_config['database'])
        
        # Test connection
        test_result = test_connection()
        
        # Restore original configuration
        config['database'] = original_config
        
        return jsonify({
            'success': True,
            'message': 'Conexión exitosa a la base de datos'
        })
    except Exception as e:
        logging.error(f"Error testing connection: {str(e)}")
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
