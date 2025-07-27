import sqlite3
import re

def reconstruct_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    schema_lines = []

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        if not columns: continue

        col_lines = []
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            not_null = "NOT NULL" if col[3] else ""
            pk = "PRIMARY KEY" if col[5] else ""
            definition = f'"{col_name}" {col_type} {not_null} {pk}'.strip()
            col_lines.append(definition)

        schema_lines.append(f'CREATE TABLE {table} (\n  ' + ',\n  '.join(col_lines) + '\n);')

    conn.close()
    return '\n\n'.join(schema_lines)

def extract_relevant_schema(full_schema, required_tables):
    relevant = []
    for table in required_tables:
        # Escape table name safely to avoid regex crashes
        safe_table = re.escape(table)
        pattern = re.compile(rf"CREATE TABLE {safe_table} \(.*?\);", re.DOTALL | re.IGNORECASE)
        match = pattern.search(full_schema)
        if match:
            relevant.append(match.group())
    return "\n\n".join(relevant)
