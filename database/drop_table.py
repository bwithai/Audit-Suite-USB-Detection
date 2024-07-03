import sqlite3


def drop_userregister_table():
    try:
        # Connect to the SQLite database
        con = sqlite3.connect("../database.sqlite")
        print("Connected to the database.")

        # Create a cursor object to execute SQL queries
        cur = con.cursor()

        # Fetch the list of tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()

        # Check if 'userregister' exists in the list of tables
        if ('userregister',) in tables:
            # Execute the query to drop the userregister table
            cur.execute("DROP TABLE userregister;")
            print("Executed DROP TABLE query.")

            # Commit the changes to the database
            con.commit()
            print("Committed changes to the database.")
        else:
            print("Table 'userregister' does not exist.")

        # Verify the table has been dropped
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()

        print("Tables in the database after dropping 'userregister':")
        for table in tables:
            print(table[0])

    except sqlite3.Error as error:
        print(f"Error while connecting to sqlite: {error}")
    finally:
        if con:
            con.close()
            print("Closed the database connection.")


# Drop the userregister table
drop_userregister_table()
