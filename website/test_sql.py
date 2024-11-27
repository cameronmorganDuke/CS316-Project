from __init__ import db

result = db.engine.execute("SELECT * FROM users")  # Use the correct table name
for row in result:
    print(row)