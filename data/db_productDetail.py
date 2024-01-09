import sqlite3
import csv

# Define the CSV file path
csv_file_path = '/home/khudi/Desktop/EcommerceAgentProject/productList.csv'

# Define the SQLite database file path
db_file_path = '/home/khudi/Desktop/db_user.db'

# Create a connection to the SQLite database
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# # Create a table in the database
# create_table_query = '''
#     CREATE TABLE IF NOT EXISTS user_table (
#         name STRING
#         ,customerID STRING
#         ,address STRING 
#         ,interested_category STRING
#         ,past_purchase_category STRING
#         ,past_purchase STRING
#         ,delivery_pending STRING
#     );
# '''
# cursor.execute(create_table_query)

# Read data from CSV and create an SQLite table
with open(csv_file_path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    header = next(csv_reader)

    # Define the table name and column names and types based on the CSV header
    table_name = 'product_detail'
    create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({", ".join([col if col != "" else "row_number" for col in header])});'
    print(create_table_query)
    cursor.execute(create_table_query)

    # Insert data into the SQLite table
    for row in csv_reader:
         # Adjust the number of placeholders based on the row length
        placeholders = ', '.join(['?' for _ in range(len(row))])

        # Construct the INSERT INTO query with the correct number of placeholders
        insert_query = f'INSERT INTO {table_name} VALUES ({placeholders});'

        try:
            # Execute the INSERT INTO query with the row values
            cursor.execute(insert_query, row)
            print("Record inserted successfully.")

        except sqlite3.Error as e:
            print(f"SQLite error: {e} - for row: {row}")

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f'Successfully created SQLite database at {db_file_path} from {csv_file_path}.')

# Connect to the SQLite database
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Query the table
table_name = 'product_detail'

select_query = f'SELECT * FROM {table_name};'

try:
    cursor.execute(select_query)
    rows = cursor.fetchall()

    # Print the query results
    if rows:
        print("Query Results:")
        for row in rows:
            print(output)
            break
    else:
        print("No results found.")

except sqlite3.Error as e:
    print(f"SQLite error: {e}")

# Close the connection
conn.close()