from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
#from database_init import Favorites

# Create an engine for a database stored in 'my_database.db'
engine = create_engine('sqlite:///instance/realestate.db', echo=True)


# Connect to the database
with engine.connect() as connection:
    
    # Example: Querying all rows from the 'users' table
    result = connection.execute(text("SELECT user_id, dtarp.reid, LOCATION_ADDR  FROM dtarp, favorites WHERE CAST(dtarp.reid AS INTEGER) = favorites.reid"))
    
    # Fetch all rows from the result
    users = result.fetchall()

    # Print each row
    for user in users:
        print(user)
