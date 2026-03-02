import sqlite3

def get_connection():
    conn = sqlite3.connect("banco.db")
    conn.row_factory = sqlite3.Row # Permite acessar colunas pelo nome (ex: row['nome'])
    # Habilita chaves estrangeiras no SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn