## Schema Manager
# This module will handle the input and do the following:
# 1. Infer the schema to get the column names and types
# 2. Check if there exists a table in the database with the same name as the CSV file 
# 3. Comparing the existing table's schema with the new data's schema to determine the appropriate action:
#    - "create": if no table exists, create a new one with the inferred schema
#    - "append": if the schemas match, append the new data to the existing table
#    - "conflict": if schemas differ, flag a potential conflict and avoid automatic insertion
# 4. Creating new tables with an auto-incrementing primary key 
# 5. Appending CSV data to existing tables when schemas match

import sqlite3

def infer_schema(df):
    dtype_map = {
        "object": "TEXT",
        "int64": "INTEGER",
        "float64": "REAL"
    }
    return {col: dtype_map.get(str(dtype), "TEXT") for col, dtype in df.dtypes.items()}


def get_existing_table(db, table_name):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    schema_info = cursor.fetchall()
    
    conn.close()
    
    if not schema_info:
        return None  # Table does not exist
    
    schema = {col[1]: col[2] for col in schema_info}  # {column_name: data_type}
    return schema

def compare_schemas(existing_schema, new_schema):
    if existing_schema is None:
        # print("No existing table found. A new table will be created.")
        return "create"  # No existing table, create new one
    
    # Ignore auto-generated id column
    existing_schema_filtered = {
        k: v for k, v in existing_schema.items() if k != "id"
    }
    
    if existing_schema_filtered == new_schema:
        # print("Existing table schema matches new data. Data will be appended.")
        return "append"  # Schemas match, append data
    
    # print("Schema conflict detected.")
    return "conflict"  # Schemas do not match, potential conflict

# Create table with primary key 'id'
def create_table(db_path, table_name, new_schema):
    columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
    columns += [f"{col} {dtype}" for col, dtype in new_schema.items()]
    create_query = f"CREATE TABLE {table_name} ({', '.join(columns)});"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(create_query)
    conn.commit()
    conn.close()

def append_csv_to_table(db_path, table_name, df):
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists='append', index=False)
    conn.close()

def resolve_schema(db_path, table_name, new_schema):
    existing_schema = get_existing_table(db_path, table_name)
    action = compare_schemas(existing_schema, new_schema)
    return action