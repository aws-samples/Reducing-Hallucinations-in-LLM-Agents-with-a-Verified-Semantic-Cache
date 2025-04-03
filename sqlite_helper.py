import sqlite3
import pandas as pd
from typing import List, Dict, Union, Optional

def list_tables(db_path: str = "lab-database.db") -> List[str]:
    """
    Lists all available tables in the SQLite database.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        List of table names in the database
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query for all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Close the connection
        conn.close()
        
        # Extract table names from the result tuples
        table_names = [table[0] for table in tables]
        return table_names
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def describe_table_schema(table_name: str, db_path: str = "lab-database.db") -> List[Dict]:
    """
    Gets column names, data types, and constraints for a specific table.
    
    Args:
        table_name: Name of the table to describe
        db_path: Path to the SQLite database file
        
    Returns:
        List of dictionaries containing column information
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query for table info using PRAGMA
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns_info = cursor.fetchall()
        
        # Check if table exists
        if not columns_info:
            conn.close()
            print(f"Table '{table_name}' not found in database")
            return []
        
        # Format the result as a list of dictionaries
        schema = []
        for column in columns_info:
            schema.append({
                "cid": column[0],
                "name": column[1],
                "type": column[2],
                "not_null": bool(column[3]),
                "default_value": column[4],
                "is_primary_key": bool(column[5])
            })
        
        # Check for foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        foreign_keys = cursor.fetchall()
        
        # Add foreign key information to the schema
        fk_dict = {}
        for fk in foreign_keys:
            fk_dict[fk[3]] = {
                "references_table": fk[2],
                "references_column": fk[4]
            }
        
        for column in schema:
            if column["name"] in fk_dict:
                column["foreign_key"] = fk_dict[column["name"]]
        
        # Close the connection
        conn.close()
        return schema
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def run_sql_query(query: str, db_path: str = "lab-database.db") -> Optional[Union[pd.DataFrame, int]]:
    """
    Executes SQL statements against the database and returns results.
    
    Args:
        query: SQL query to execute
        db_path: Path to the SQLite database file
        
    Returns:
        For SELECT queries: pandas DataFrame with results
        For INSERT/UPDATE/DELETE: Number of affected rows
        For errors: None
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        
        # Determine query type
        query_type = query.strip().upper().split()[0]
        
        if query_type == "SELECT":
            # For SELECT queries, return a pandas DataFrame
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        else:
            # For other queries (INSERT, UPDATE, DELETE), execute and return row count
            cursor = conn.cursor()
            cursor.execute(query)
            affected_rows = cursor.rowcount
            
            # Commit changes and close connection
            conn.commit()
            conn.close()
            
            return affected_rows
            
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
    except pd.io.sql.DatabaseError as e:
        print(f"pandas SQL error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def get_sample_rows(table_name: str, db_path: str = "lab-database.db") -> Optional[Union[pd.DataFrame, int]]:
    """
    Gets 10 sample rows of data from a table.
    
    Args:
        table_name: Name of the table to get sample rows
        db_path: Path to the SQLite database file (defaults to lab-database.db)
        
    Returns:
        pandas DataFrame containing 10 rows from the table, or None if an error occurs
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        
        # Query to get 10 sample rows
        query = f"SELECT * FROM {table_name} LIMIT 10;"
        
        # Execute the query and get results as a DataFrame
        df = pd.read_sql_query(query, conn)
        
        # Close the connection
        conn.close()
        
        # Return the DataFrame
        return df
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
    except pd.io.sql.DatabaseError as e:
        print(f"pandas SQL error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None