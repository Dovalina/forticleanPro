# Dashboard de Pedidos Pendientes para Clic Laguna

## Descripción
Este sistema permite visualizar en tiempo real los pedidos pendientes de surtir desde la base de datos Microsip, con actualizaciones automáticas cada 5 minutos.

## Características
- Visualización de pedidos pendientes en una tabla clara y ordenada
- Actualización automática de datos cada 5 minutos
- Sistema de acceso con autenticación de usuarios
- Panel de configuración para ajustar la conexión a la base de datos
- Gestión de usuarios con diferentes niveles de acceso

## Requisitos
- Python 3.8 o superior
- Conexión a la base de datos Firebird de Microsip
- Cliente Firebird instalado en el sistema

## Instalación

### Método Automático
1. Ejecuta el script de instalación:
   ```
   python install.py
   ```
2. Sigue las instrucciones en pantalla para configurar la conexión a tu base de datos

### Método Manual
1. Instala las dependencias:
   ```
   pip install flask pyodbc fdb firebird-driver pyyaml
   ```
2. Configura la información de conexión a la base de datos en el archivo `config.yaml`

## Uso
1. Inicia la aplicación:
   - En Windows: Ejecuta `iniciar_dashboard.bat`
   - En Linux/Mac: Ejecuta `./iniciar_dashboard.sh`
2. Abre un navegador web y visita: `http://localhost:5000`
3. Inicia sesión con las credenciales proporcionadas

## Acceso
- **Superadmin**: usuario: `admin`, contraseña: `admin123`
- **Usuario Normal**: usuario: `usuario`, contraseña: `usuario123`

## Configuración Avanzada
Para modificar la configuración del sistema:
1. Inicia sesión como superadmin
2. Ve a la sección de "Configuración" en el menú superior
3. Ajusta los parámetros según sea necesario

### Conexión Remota al Servidor
El dashboard está preconfigurado para conectarse al servidor:
- Servidor: forticlean.ddns.net
- Ruta BD: C:/Microsip/EMPRESA.FDB
- Usuario: SYSDBA
- Contraseña: 050587

También puedes acceder al servidor por escritorio remoto:
- Dirección: forticlean.ddns.net:4040
- Usuario: Administrador
- Contraseña: Forti2021+

## Solución de Problemas
- **Error de conexión a la base de datos**: Verifica que los datos de conexión sean correctos y que el cliente Firebird esté instalado correctamente.
- **Problemas de acceso**: Asegúrate de estar usando las credenciales correctas.

---

Desarrollo: Sergio Dovalina (checodovalina@gmail.com)
Exclusivo para Clic Laguna © 2025