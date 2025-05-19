import os
import yaml
import logging

# Default configuration
DEFAULT_CONFIG = {
    'database': {
        'driver': 'Firebird/InterBase(r) driver',
        'dsn': 'localhost:C:/Microsip/EMPRESA.FDB',
        'user': 'SYSDBA',
        'password': 'masterkey',
        'charset': 'UTF8',
        'use_sample_data': True,  # Configurado para usar datos de ejemplo permanentemente
        'query': """
            SELECT 
              p.PEDIDO AS pedido,
              c.NOMBRE AS cliente,
              p.FECHA AS fecha,
              p.HORA AS hora,
              v.NOMBRE AS vendedora,
              p.ESTATUS AS estatus
            FROM 
              PEDIDOS p
            JOIN 
              CLIENTES c ON p.CLIENTE_ID = c.CLIENTE_ID
            JOIN
              VENDEDORES v ON p.VENDEDOR_ID = v.VENDEDOR_ID
            WHERE 
              p.ESTATUS = 'P' OR p.ESTATUS = 'En proceso'
            ORDER BY 
              p.FECHA DESC, p.HORA DESC
        """
    },
    'application': {
        'refresh_interval': 300,  # 5 minutes in seconds
        'title': 'Dashboard de Pedidos Pendientes'
    },
    'users': {
        'admin': {
            'password': 'pbkdf2:sha256:150000$q8DNDrQw$eaa2a4e8d583e6e756a83c6e4feece1011d363d3489efe677cbba33c8fc77c24',
            'role': 'admin'
        }
    }
}

CONFIG_PATH = 'config.yaml'

def load_config():
    """
    Load configuration from config.yaml file or create a default one if not exists
    """
    # Check if configuration file exists
    if not os.path.exists(CONFIG_PATH):
        logging.warning(f"Configuration file {CONFIG_PATH} not found. Creating default config.")
        create_default_config(CONFIG_PATH)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            logging.info("Configuration loaded successfully")
            return config
    except Exception as e:
        logging.error(f"Error loading configuration: {str(e)}")
        return DEFAULT_CONFIG

def update_config(config):
    """
    Update the configuration file with new settings
    """
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as file:
            yaml.dump(config, file, default_flow_style=False)
        logging.info("Configuration updated successfully")
        return True
    except Exception as e:
        logging.error(f"Error updating configuration: {str(e)}")
        return False

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
