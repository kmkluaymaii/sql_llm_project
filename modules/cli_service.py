# User will run python3 cli_service.py "user question" xxx.csv to get the SQL query output
import sqlite3
import sys

from data_loader import load_data, insert_data
from schema_manager import append_csv_to_table, get_existing_table, create_table, resolve_schema, infer_schema
from llm_interface import generate_sql
from query_service import execute_sql, cli_loop

if __name__ == "__main__":
    # Perform data_loader 
    if len(sys.argv) != 3:
        print("Usage: python3 cli_service.py \"user question\" \"csv_file_path\"")
        sys.exit(1)
    user_query = sys.argv[1]
    csv_file_path = sys.argv[2]
    db_file_path = f"data/music_movie.db"
    data = load_data(csv_file_path)
    table_name = f"{csv_file_path.split('/')[-1].split('.')[0]}_table"
    print(f"Data loaded successfully into {db_file_path}!")
    
    # Perform schema_manager
    existing_table = get_existing_table(db_file_path, table_name)
    new_schema = infer_schema(data)
    action = resolve_schema(db_file_path, table_name, new_schema)
    if action == "create":
        create_table(db_file_path, table_name, new_schema)
        append_csv_to_table(db_file_path, table_name, data)
        print(f"Table '{table_name}' created successfully.")

    elif action == "append":
        print("Schema matches. Skipping insert to avoid duplicates.")
    
    elif action == "conflict":
        print(f"Schema conflict detected for table '{table_name}'!")

    print(f"Schema Manager Done!")
    
    # Perform llm_interface
    schema_dict = {table_name: get_existing_table(db_file_path, table_name)}

    print("Generating SQL...")

    sql, explanation = generate_sql(user_query, schema_dict)

    # Ensure response is received before printing
    if sql:
        print(f"\nGenerated SQL: {sql}")
    else:
        print("\nNo SQL generated.")

    if explanation:
        print(f"\nExplanation: {explanation}\n")
    else:
        print("\nNo explanation provided.")
        
    # Perform query_service
    df, err = execute_sql(db_file_path, sql)
    if err:
        print(err)
    else:
        print(df)
    
    cli_loop(db_file_path)
    