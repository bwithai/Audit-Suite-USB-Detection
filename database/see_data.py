import sqlite3

# Connect to the SQLite database
con = sqlite3.connect("../database.sqlite")

# Create a cursor object
cur = con.cursor()

# Define the query to select all data from the register_user table
query = "SELECT * FROM detected_devices"

# Execute the query
cur.execute(query)

# Fetch all rows from the executed query
rows = cur.fetchall()

# Print the column names (optional)
column_names = [description[0] for description in cur.description]
print("Column names:", column_names)

# Print each row
for row in rows:
    print(row)

# Close the cursor and the connection
cur.close()
con.close()
