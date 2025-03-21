import cx_Oracle
import pandas as pd
import os
import multiprocessing

# Initialize Oracle client
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\muppa\instantclient_21_12")

# Database connection details
DB_CONFIG = {
    "user": "your_user",
    "password": "yourpassword",
    "dsn": cx_Oracle.makedsn("localhost", 1521, service_name="XE"),
    "encoding": "UTF-8"
}

# List of tables to extract data from
custom_tables = ["SAMPLE_TABLE", "EMPLOYEES", "ORDERS"]  # Replace with your actual table names

# Directory to store CSV files
output_dir = "oracle_selected_tables_csv"
os.makedirs(output_dir, exist_ok=True)

# Create a connection pool for better performance
POOL_SIZE = min(4, len(custom_tables))  # Adjust number of connections dynamically
pool = cx_Oracle.SessionPool(min=POOL_SIZE, max=POOL_SIZE * 2, increment=1, **DB_CONFIG)

def fetch_and_write_table(table):
    """Fetch data from a table and write it to a CSV file efficiently."""
    try:
        # Get a connection from the pool
        connection = pool.acquire()
        cursor = connection.cursor()

        print(f"🔄 Processing table: {table}")

        # Fetch column names and data types
        cursor.execute(f"SELECT column_name FROM user_tab_columns WHERE table_name = '{table}'")
        columns = [col[0] for col in cursor.fetchall()]

        # Fetch table data efficiently
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()

        if not rows:
            print(f"⚠️ No data found in {table}. Skipping.")
            return
        
        # Convert data to DataFrame
        df = pd.DataFrame(rows, columns=columns)

        # Write data to CSV using pandas (faster than csv.writer)
        csv_filename = os.path.join(output_dir, f"{table}.csv")
        df.to_csv(csv_filename, index=False, encoding="utf-8")

        print(f"✅ Data from {table} written to {csv_filename}")

    except cx_Oracle.DatabaseError as e:
        print(f"❌ Error processing table {table}: {e}")

    finally:
        cursor.close()
        pool.release(connection)  # Return connection to the pool

if __name__ == "__main__":
    # Use multiprocessing with dynamic number of workers
    num_workers = min(multiprocessing.cpu_count(), len(custom_tables))  
    with multiprocessing.Pool(processes=num_workers) as pool:
        pool.map(fetch_and_write_table, custom_tables)

    print("🎉 All tables have been processed in parallel using connection pooling!")
