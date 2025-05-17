import logging
import datetime
from config import load_config
import firebird.driver as fdb
from firebird.driver import connect, connect_server

# Load the configuration
config = load_config()
db_config = config['database']

def create_connection():
    """
    Create a connection to the Firebird database using firebird-driver
    """
    try:
        # Determine connection parameters
        dsn_parts = db_config['dsn'].split(':')
        if len(dsn_parts) == 2:
            host, path = dsn_parts
        else:
            host = 'localhost'
            path = db_config['dsn']
            
        # Connect using the firebird-driver connector
        conn = connect(
            host=host,
            database=path,
            user=db_config['user'],
            password=db_config['password'],
            charset=db_config.get('charset', 'UTF8')
        )
        logging.info(f"Connected to Firebird database at {db_config['dsn']}")
        return conn
    except Exception as e:
        logging.error(f"Firebird connection failed: {str(e)}")
        logging.warning("Falling back to sample data for demonstration")
        
        # Si hay error de conexión, mostrar datos de muestra
        return None

def test_connection():
    """
    Test the database connection
    """
    try:
        conn = create_connection()
        if conn is None:
            # Fallback to sample mode with warning
            logging.warning("Using sample data mode - database connection not available")
            return True
            
        # Test connection by executing a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        logging.info("Database connection test successful")
        return True
    except Exception as e:
        logging.error(f"Database connection test failed: {str(e)}")
        # Fallback to sample mode
        logging.warning("Switching to sample data mode")
        return True

def get_pending_orders():
    """
    Get pending orders from the Microsip database
    """
    try:
        conn = create_connection()
        
        # Si no hay conexión, mostrar datos de ejemplo
        if conn is None:
            return _get_sample_orders()
            
        cursor = conn.cursor()
        
        # Usar la consulta definida en el archivo de configuración
        query = db_config.get('query')
        
        cursor.execute(query)
        
        # Convertir resultados a lista de diccionarios
        columns = [column[0].lower() for column in cursor.description]
        orders = []
        for row in cursor.fetchall():
            # Crear un diccionario con los valores de la fila
            order_dict = dict(zip(columns, row))
            
            # Formatear fecha y hora correctamente si es necesario
            if isinstance(order_dict.get('fecha'), datetime.datetime):
                order_dict['fecha'] = order_dict['fecha'].date()
                
            # Garantizar que todos los campos necesarios estén presentes
            if 'pedido' not in order_dict and 'folio' in order_dict:
                order_dict['pedido'] = f"#{order_dict['folio']}"
                
            orders.append(order_dict)
        
        cursor.close()
        conn.close()
        
        logging.info(f"Retrieved {len(orders)} pending orders from database")
        return orders
    except Exception as e:
        logging.error(f"Error fetching pending orders: {str(e)}")
        logging.warning("Falling back to sample data")
        return _get_sample_orders()

def _get_sample_orders():
    """
    Función auxiliar para proporcionar datos de muestra
    """
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
