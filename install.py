#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de instalación para el Dashboard de Pedidos Pendientes
Este script automatiza la instalación de dependencias y configuración inicial
"""

import os
import sys
import shutil
import subprocess
import platform
import time

# Colores para la consola
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
END = '\033[0m'

def print_header():
    """Imprime el encabezado del instalador"""
    print(f"\n{BLUE}{BOLD}======================================================{END}")
    print(f"{BLUE}{BOLD}  INSTALADOR DEL DASHBOARD DE PEDIDOS - CLIC LAGUNA  {END}")
    print(f"{BLUE}{BOLD}======================================================{END}\n")

def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    print(f"{BOLD}[1/6] Verificando versión de Python...{END}")
    
    major, minor = sys.version_info.major, sys.version_info.minor
    if major < 3 or (major == 3 and minor < 8):
        print(f"{RED}Error: Se requiere Python 3.8 o superior. Versión actual: {major}.{minor}{END}")
        sys.exit(1)
    print(f"{GREEN}✓ Usando Python {major}.{minor} - compatible{END}")

def install_dependencies():
    """Instala las dependencias necesarias"""
    print(f"\n{BOLD}[2/6] Instalando dependencias de Python...{END}")
    
    dependencies = [
        'flask',
        'pyodbc',
        'fdb',
        'firebird-driver',
        'pyyaml',
    ]
    
    try:
        for package in dependencies:
            print(f"- Instalando {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{GREEN}✓ Dependencias instaladas correctamente{END}")
    except subprocess.CalledProcessError:
        print(f"{RED}Error al instalar algunas dependencias.{END}")
        print("Intenta ejecutar manualmente: pip install flask pyodbc fdb firebird-driver pyyaml")

def check_firebird():
    """Comprueba si el cliente de Firebird está instalado o proporciona instrucciones"""
    print(f"\n{BOLD}[3/6] Verificando cliente Firebird...{END}")
    
    system = platform.system()
    
    if system == "Windows":
        # En Windows verificamos archivos comunes del cliente Firebird
        paths_to_check = [
            r"C:\Program Files\Firebird\Firebird_2_5\bin\fbclient.dll",
            r"C:\Program Files\Firebird\Firebird_3_0\bin\fbclient.dll",
            r"C:\Program Files (x86)\Firebird\Firebird_2_5\bin\fbclient.dll",
            r"C:\Program Files (x86)\Firebird\Firebird_3_0\bin\fbclient.dll",
        ]
        
        found = False
        for path in paths_to_check:
            if os.path.exists(path):
                found = True
                print(f"{GREEN}✓ Cliente Firebird encontrado en: {path}{END}")
                break
        
        if not found:
            print(f"{YELLOW}! Cliente Firebird no encontrado.{END}")
            print(f"  {YELLOW}Necesitas instalar Firebird para conectarte a la base de datos.{END}")
            print(f"  {YELLOW}Descarga desde: https://firebirdsql.org/en/firebird-3-0/{END}")
    else:
        # En Linux y Mac es más complejo verificar, así que solo damos instrucciones
        print(f"{YELLOW}! En {system}, necesitas instalar el cliente Firebird manualmente.{END}")
        if system == "Linux":
            print("  Ejecuta: sudo apt-get install firebird3.0-utils")
        elif system == "Darwin":  # MacOS
            print("  Instala mediante Homebrew: brew install firebird")

def configure_database():
    """Configura la conexión a la base de datos"""
    print(f"\n{BOLD}[4/6] Configurando conexión a la base de datos...{END}")
    
    config_path = "config.yaml"
    
    # Verificar si tenemos que configurar desde cero
    if os.path.exists(config_path):
        print(f"{YELLOW}! Se encontró un archivo de configuración existente.{END}")
        modify = input("¿Deseas modificar la configuración? (s/n): ").lower() == 's'
        if not modify:
            print("Manteniendo configuración actual.")
            return
    
    print("\nIntroduce los datos de conexión a la base de datos Microsip:")
    
    # Server puede ser localhost o una IP
    server = input("Servidor (localhost o IP): ") or "localhost"
    
    # Ruta a la base de datos
    default_path = r"C:\Microsip\EMPRESA.FDB"
    db_path = input(f"Ruta a la base de datos [{default_path}]: ") or default_path
    
    # Si la ruta tiene espacios y no está entre comillas, la ajustamos
    if " " in db_path and not (db_path.startswith('"') and db_path.endswith('"')):
        db_path = f'"{db_path}"'
    
    # Usuario y contraseña (valores por defecto para Firebird)
    user = input("Usuario [SYSDBA]: ") or "SYSDBA"
    password = input("Contraseña [masterkey]: ") or "masterkey"
    
    # Crear o actualizar la sección de base de datos en el archivo de configuración
    from config import load_config, update_config
    config = load_config()
    
    config['database']['dsn'] = f"{server}:{db_path}"
    config['database']['user'] = user
    config['database']['password'] = password
    
    update_config(config)
    print(f"{GREEN}✓ Configuración de base de datos actualizada{END}")

def create_shortcut():
    """Crea accesos directos para facilitar la ejecución"""
    print(f"\n{BOLD}[5/6] Creando accesos directos...{END}")
    
    system = platform.system()
    
    if system == "Windows":
        # Crear archivo BAT para Windows
        with open("iniciar_dashboard.bat", "w") as batch_file:
            batch_file.write('@echo off\n')
            batch_file.write('title Dashboard de Pedidos Pendientes\n')
            batch_file.write('echo Iniciando Dashboard de Pedidos Pendientes...\n')
            batch_file.write('echo ------------------------------------------\n')
            batch_file.write('python main.py\n')
            batch_file.write('pause\n')
        
        print(f"{GREEN}✓ Creado acceso directo: iniciar_dashboard.bat{END}")
    else:
        # Crear script bash para Linux/Mac
        with open("iniciar_dashboard.sh", "w") as shell_file:
            shell_file.write('#!/bin/bash\n')
            shell_file.write('echo "Iniciando Dashboard de Pedidos Pendientes..."\n')
            shell_file.write('echo "------------------------------------------"\n')
            shell_file.write('python3 main.py\n')
        
        # Hacer el script ejecutable
        os.chmod("iniciar_dashboard.sh", 0o755)
        print(f"{GREEN}✓ Creado acceso directo: iniciar_dashboard.sh{END}")

def finish_installation():
    """Muestra instrucciones finales y finaliza la instalación"""
    print(f"\n{BOLD}[6/6] Instalación completada{END}")
    
    system = platform.system()
    if system == "Windows":
        start_cmd = "iniciar_dashboard.bat"
    else:
        start_cmd = "./iniciar_dashboard.sh"
    
    print(f"\n{GREEN}{BOLD}¡Instalación exitosa!{END}")
    print(f"\nPara iniciar el dashboard, ejecuta: {BLUE}{start_cmd}{END}")
    print(f"\nCredenciales de acceso:")
    print(f"  {YELLOW}Superadmin:{END} usuario 'admin', contraseña 'admin123'")
    print(f"  {YELLOW}Usuario normal:{END} usuario 'usuario', contraseña 'usuario123'")
    
    print(f"\n{BLUE}{BOLD}¡Gracias por usar el Dashboard de Pedidos Pendientes de Clic Laguna!{END}")
    print(f"\nDesarrollo: Sergio Dovalina (checodovalina@gmail.com)")

def main():
    """Función principal del instalador"""
    try:
        print_header()
        check_python_version()
        install_dependencies()
        check_firebird()
        
        # Importamos después de instalar dependencias
        import yaml
        configure_database()
        create_shortcut()
        finish_installation()
        
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Instalación cancelada por el usuario.{END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Error durante la instalación: {e}{END}")
        print(f"{YELLOW}Por favor contacta al soporte técnico.{END}")
        sys.exit(1)

if __name__ == "__main__":
    main()