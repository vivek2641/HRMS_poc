import mysql.connector
from global_config import MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_HOST,MYSQL_USER

# --- Database Connection Helper ---
def query_db(query: str, params: tuple = ()): 
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )
    cursor = conn.cursor()
    cursor.execute(query, params)
    columns = [col[0] for col in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return results
