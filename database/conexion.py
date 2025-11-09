import mysql.connector

def get_db_connection():
    """
    Retorna una conexión a MySQL. Rellena las credenciales según tu entorno.
    """
    return mysql.connector.connect(
        host="localhost",       
        user="root",            
        password="root",    
        database="clinica_dental",  
        autocommit=True
    )
