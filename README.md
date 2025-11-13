## Características Principales

*   **Gestión de Pacientes:** Creación, edición y visualización de pacientes en una interfaz moderna de tarjetas.
*   **Agendamiento Inteligente de Citas:**
    *   Búsqueda de horarios en fechas específicas.
    *   Búsqueda de la "próxima cita disponible" basada en patrones (ej. "martes por la tarde").
    *   Lógica de negocio compleja manejada por Prolog para validar la disponibilidad del dentista, las preferencias del paciente y los filtros dinámicos.
*   **Interfaz Moderna:** Construida con `ttkbootstrap` para una apariencia profesional y responsiva.
*   **Seguridad:** Sistema de inicio de sesión con hashing de contraseñas (`bcrypt`).

## Prerrequisitos de Software

Para ejecutar esta aplicación, necesitarás tener instalado el siguiente software en tu sistema:

2.  **Python:**.
    
3.  **MySQL Community Server & Workbench:** El sistema de base de datos.
    
4.  **SWI-Prolog:** El motor de reglas lógicas.
    *   **Importante:** Durante la instalación, asegúrate de marcar la opción **"Add swipl to the system PATH"**.

## Guía de Instalación y Ejecución


2.  **Configurar la Base de Datos**
    *   Abre **MySQL Workbench** y conéctate a tu servidor de base de datos.
    *   Abre el archivo `BaseDatosClinicaDental.sql` del proyecto y ejecuta el script completo. Esto creará la base de datos `clinica_dental` y todas las tablas necesarias.

3.  **Configurar el Entorno de Python**
    *   **Crear el entorno virtual:**
   
        py -m venv venv

    *   **Activar el entorno (Windows):**

        .\venv\Scripts\activate

    *   **Instalar las dependencias:**

        pip install -r requirements.txt
        ```

4.  **Configurar la Conexión a la Base de Datos**
    *   Abre el archivo `database/conexion.py` en un editor de código.
    *   Modifica la línea `password="tu_contraseña_aqui"` para que coincida con la contraseña de tu usuario `root` de MySQL.


## Iniciar la Aplicación

Una vez completada la instalación, inicia el programa con:

py main.py

### Credenciales de Inicio de Sesión
*   **Usuario:** `admin`
*   **Contraseña:** `admin123`