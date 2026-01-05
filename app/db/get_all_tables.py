import sqlite3
from app.core.config import settings

def get_all_tables(db_path:str)->list[str]:

    conn=sqlite3.connect(settings.DB_PATH)
    cursor =conn.cursor()
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%';
    """)
    tables=[]
    for i in cursor:
        tables.append(i[0])
    
    return tables

def get_table_schema(db_path: str, table:str) -> list[dict]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(f"PRAGMA table_info({table});")

    columns = cursor.fetchall()
    conn.close()

    schema = []
    for cid, name, dtype, notnull, default, pk in columns:
        schema.append({
            "column": name,
            "type": dtype,
            "not_null": bool(notnull),
            "primary_key": bool(pk),
            "default": default
        })

    return schema

def all_tables_schema(tables):
    tables_schema_dictionary={}

    for table in tables:
       table_schema= get_table_schema(settings.DB_PATH,table)
       tables_schema_dictionary[table]=table_schema
    
    return tables_schema_dictionary


def get_all_tables_schema():
    tables=get_all_tables(settings.DB_PATH)
   
    results=all_tables_schema(tables)
    
    
    return results

def execute_sql(sql: str):
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(sql)
    rows = cursor.fetchall()

    result = [dict(row) for row in rows]

    conn.close()
    return result
