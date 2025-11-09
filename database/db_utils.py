from typing import List, Dict

def fetch_all_dict(cursor) -> List[Dict]:
    """Convierte los resultados de un cursor.fetchall() a una lista de diccionarios."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]