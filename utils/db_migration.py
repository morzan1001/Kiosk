#!/usr/bin/env python3

import sqlite3
import psycopg2
import sys
from typing import List

def get_sqlite_tables(sqlite_conn) -> List[str]:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']

def get_table_schema(sqlite_conn, table_name: str) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    
    type_mapping = {
        'INTEGER': 'INTEGER',
        'TEXT': 'TEXT',
        'REAL': 'REAL',
        'BLOB': 'BYTEA',
        'NUMERIC': 'NUMERIC'
    }
    
    column_defs = []
    for col in columns:
        col_name = col[1]
        col_type = col[2].upper()
        pg_type = type_mapping.get(col_type, 'TEXT')
        not_null = ' NOT NULL' if col[3] else ''
        column_defs.append(f"{col_name} {pg_type}{not_null}")
    
    return f"CREATE TABLE {table_name} ({', '.join(column_defs)});"

def migrate_data(sqlite_conn, pg_conn, table_name: str):
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print(f"Table {table_name} is empty, skip...")
        return

    sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in sqlite_cursor.fetchall()]
    
    placeholders = ', '.join(['%s'] * len(columns))
    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    
    pg_cursor.executemany(insert_sql, rows)
    print(f"Migrates {len(rows)} rows for table {table_name}")

def main():
    SQLITE_DB = "../src/database/kiosk.db"
    PG_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'kiosk',
        'user': 'kiosk',
        'password': 'your_password_here'
    }
    
    try:
        print("Connecting to SQLite-Datenbase...")
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        
        print("Connecting to PostgreSQL-Datenbase...")
        pg_conn = psycopg2.connect(**PG_CONFIG)
        pg_conn.autocommit = False
        
        tables = get_sqlite_tables(sqlite_conn)
        print(f"Tables found: {tables}")
        
        pg_cursor = pg_conn.cursor()
        
        for table in tables:
            print(f"\Migrate table: {table}")
            
            schema_sql = get_table_schema(sqlite_conn, table)
            print(f"Create table with schema: {schema_sql}")
            
            try:
                pg_cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                pg_cursor.execute(schema_sql)
                pg_conn.commit()
                
                migrate_data(sqlite_conn, pg_conn, table)
                pg_conn.commit()
                
            except Exception as e:
                print(f"Error with table {table}: {e}")
                pg_conn.rollback()
                continue
        
        print("\nMigration completed!")
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        sys.exit(1)
    except psycopg2.Error as e:
        print(f"PostgreSQL error: {e}")
        sys.exit(1)
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    main()