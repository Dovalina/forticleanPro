#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para exportar datos de pedidos pendientes de la base de datos Firebird
a un archivo JSON que puede ser usado por el dashboard.

Este script debe ejecutarse en una máquina que tenga instalado el cliente Firebird.
"""

import os
import sys
import json
import logging
import datetime
from config import load_config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def conectar_firebird(config):
    """Conecta a la base de datos Firebird usando fdb"""
    try:
        import fdb
        
        # Obtener configuración de la base de datos
        dsn = config['database']['dsn']
        user = config['database']['user']
        password = config['database']['password']
        
        # Intentar conexión
        logging.info(f"Conectando a {dsn}...")
        connection = fdb.connect(
            dsn=dsn,
            user=user,
            password=password,
            charset='UTF8'
        )
        logging.info("Conexión exitosa")
        return connection
    except ImportError:
        logging.error("No se pudo importar el módulo fdb. Asegúrate de tener instalado el cliente Firebird.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error al conectar a la base de datos: {str(e)}")
        sys.exit(1)

def obtener_pedidos(connection, config):
    """Obtiene los pedidos pendientes de la base de datos"""
    try:
        cursor = connection.cursor()
        
        # Usar la consulta definida en la configuración
        query = config['database']['query']
        
        logging.info("Ejecutando consulta para obtener pedidos pendientes...")
        cursor.execute(query)
        
        # Convertir a lista de diccionarios con nombres de columnas
        column_names = [desc[0].lower() for desc in cursor.description]
        result = []
        
        for row in cursor.fetchall():
            # Crear un diccionario para cada fila
            row_dict = {}
            for i, value in enumerate(row):
                # Convertir fechas y tiempos a cadenas
                if isinstance(value, (datetime.date, datetime.time, datetime.datetime)):
                    value = value.isoformat()
                row_dict[column_names[i]] = value
            result.append(row_dict)
        
        logging.info(f"Se obtuvieron {len(result)} pedidos pendientes")
        return result
    except Exception as e:
        logging.error(f"Error al obtener datos: {str(e)}")
        return []

def guardar_json(pedidos, timestamp=None):
    """Guarda los pedidos en un archivo JSON"""
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Crear estructura del JSON
    data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "pedidos": pedidos,
        "total": len(pedidos)
    }
    
    # Guardar en archivo
    filename = "datos_pedidos.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Datos guardados en {filename}")
        return filename
    except Exception as e:
        logging.error(f"Error al guardar archivo JSON: {str(e)}")
        return None

def solicitar_credenciales():
    """Solicita credenciales de acceso al usuario"""
    print("\nPor favor, proporciona las credenciales de acceso a la base de datos:")
    servidor = input("Servidor (ej. localhost, IP o nombre de host): ")
    ruta_bd = input("Ruta a la base de datos (ej. C:/Microsip/EMPRESA.FDB): ")
    usuario = input("Usuario: ")
    contrasena = input("Contraseña: ")
    
    # Validar entradas
    if not servidor or not ruta_bd or not usuario or not contrasena:
        print("Error: Todos los campos son obligatorios")
        return None
    
    # Crear configuración temporal
    config_temp = {
        'database': {
            'dsn': f"{servidor}:C:/microsip datos/forticlean.fdb",
            'user': usuario,
            'password': contrasena,
            'charset': 'UTF8',
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
        }
    }
    
    return config_temp

def main():
    try:
        # Mostrar encabezado
        print("\n======================================================")
        print("  EXPORTADOR DE DATOS PARA DASHBOARD DE PEDIDOS")
        print("======================================================\n")
        
        # Cargar configuración
        config = load_config()
        
        # Intentar conexión inicial
        try:
            connection = conectar_firebird(config)
        except Exception as e:
            print(f"\nError al conectar a la base de datos: {str(e)}")
            print("\nLas credenciales en el archivo de configuración no son válidas.")
            
            # Preguntar si desea intentar con otras credenciales
            retry = input("\n¿Deseas intentar con otras credenciales? (s/n): ").lower()
            if retry == 's':
                nuevas_credenciales = solicitar_credenciales()
                if nuevas_credenciales:
                    # Actualizar configuración temporalmente
                    config['database'] = nuevas_credenciales['database']
                    
                    # Preguntar si desea guardar
                    guardar = input("\n¿Deseas guardar estas credenciales para usos futuros? (s/n): ").lower()
                    if guardar == 's':
                        from config import update_config
                        update_config(config)
                        print("Configuración actualizada y guardada.")
                    
                    # Intentar conectar con nuevas credenciales
                    connection = conectar_firebird(config)
                else:
                    print("No se proporcionaron credenciales válidas.")
                    sys.exit(1)
            else:
                print("Operación cancelada.")
                sys.exit(1)
        
        # Obtener pedidos
        pedidos = obtener_pedidos(connection, config)
        
        if pedidos:
            # Guardar en JSON
            json_file = guardar_json(pedidos)
            
            if json_file:
                print(f"\nExportación exitosa: {len(pedidos)} pedidos guardados en {json_file}")
                print("\nPara usar estos datos:")
                print("1. Copia este archivo al servidor donde está alojado el dashboard")
                print("2. El dashboard detectará automáticamente el archivo y mostrará los datos\n")
        else:
            print("\nNo se encontraron pedidos pendientes para exportar")
        
        # Cerrar conexión
        if connection:
            connection.close()
            
    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")
        print(f"\nOcurrió un error inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()