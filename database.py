import logging
import datetime
from config import load_config

# Load the configuration
config = load_config()
db_config = config['database']

def create_connection():
    """
    Mock function for database connection until Firebird issues are resolved
    """
    logging.info("Using sample data for demonstration")
    return None

def test_connection():
    """
    Test connection always returns True when using sample data
    """
    return True

def get_pending_orders():
    """
    Return sample orders data with the structure matching the required format
    """
    try:
        # Sample data based on the screenshot provided
        current_date = datetime.datetime.now()
        yesterday = current_date - datetime.timedelta(days=1)
        two_days_ago = current_date - datetime.timedelta(days=2)
        
        orders = [
            {
                'pedido': '#1245',
                'cliente': 'Muma',
                'fecha': two_days_ago.date(),
                'hora': '10:23',
                'vendedora': 'Sofía',
                'estatus': 'Pendiente'
            },
            {
                'pedido': '#1246',
                'cliente': 'Oxxo Nte',
                'fecha': yesterday.date(),
                'hora': '09:50',
                'vendedora': 'Laura',
                'estatus': 'En proceso'
            },
            {
                'pedido': '#1247',
                'cliente': 'Coca Torreón',
                'fecha': current_date.date(),
                'hora': '11:05',
                'vendedora': 'Diego',
                'estatus': 'Terminado'
            }
        ]
        
        logging.info(f"Returning {len(orders)} sample orders")
        return orders
    except Exception as e:
        logging.error(f"Error generating sample orders: {str(e)}")
        raise
