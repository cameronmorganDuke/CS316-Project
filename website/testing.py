from sqlalchemy import create_engine, text
#from database_init import Favorites

# Create an engine for a database stored in 'my_database.db'
engine = create_engine('sqlite:///instance/master.db', echo=True)


# Connect to the database
with engine.connect() as connection:
    
    # Example: Querying all rows from the 'users' table
    result = connection.execute(text("SELECT * from Note"))
    
    # Fetch all rows from the result
    users = result.fetchall()

    # Print each row
    for user in users:
        print(user)
