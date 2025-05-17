import os
import yaml
import logging

# Default configuration
DEFAULT_CONFIG = {
    'database': {
        'driver': 'Firebird/InterBase(r) driver',
        'dsn': 'localhost:C:/path/to/database.fdb',
        'user': 'SYSDBA',
        'password': 'masterkey',
        'charset': 'UTF8'
    },
    'application': {
        'refresh_interval': 300,  # 5 minutes in seconds
        'title': 'Dashboard de Pedidos Pendientes'
    }
}

def load_config():
    """
    Load configuration from config.yaml file or create a default one if not exists
    """
    config_path = 'config.yaml'
    
    # Check if configuration file exists
    if not os.path.exists(config_path):
        logging.warning(f"Configuration file {config_path} not found. Creating default config.")
        create_default_config(config_path)
        return DEFAULT_CONFIG
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            logging.info("Configuration loaded successfully")
            return config
    except Exception as e:
        logging.error(f"Error loading configuration: {str(e)}")
        return DEFAULT_CONFIG

def create_default_config(config_path):
    """
    Create a default configuration file
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(DEFAULT_CONFIG, file, default_flow_style=False)
        logging.info(f"Default configuration created at {config_path}")
    except Exception as e:
        logging.error(f"Error creating default configuration: {str(e)}")
