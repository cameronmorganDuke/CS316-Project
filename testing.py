from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.orm import sessionmaker

def get_tables(db_path):
    # Create the engine
    engine = create_engine(f'sqlite:///{db_path}')

    # Reflect the existing database into a new MetaData object
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # Print all table names
    print(metadata.tables.keys())
    

def get_db_schema(db_path):
    
    # Create an engine that connects to the SQLite database
    engine = create_engine(f'sqlite:///{db_path}')

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Reflect the tables from the database
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # You can now access the tables and work with them
    for table_name, table in metadata.tables.items():
        print(f'Table: {table_name}')
        for column in table.columns:
            print(f'Column: {column.name}, Type: {column.type}')

    # Example: querying a table (replace 'your_table' with an actual table name)
    your_table = Table('your_table_name', metadata, autoload_with=engine)
    results = session.query(your_table).all()

    # for row in results:
    #     print(row)
    
def query_db(db_path, query):
    engine = create_engine(f'sqlite:///{db_path}')
    with engine.connect() as connection:
        result = connection.execute(text(query))
    rows = result.fetchall()
    for row in rows:
        print(row)
    
if __name__ == "__main__":
    query = """
        SELECT a1.REID, a1.LOCATION_ADDR, a1.OWNER_MAIL_1, a1.OWNER_MAIL_CITY, a1.OWNER_MAIL_STATE, a1.OWNER_MAIL_ZIP
        FROM your_table_name a1, your_table_name a2
        WHERE a1.REID <> a2.REID AND a2.LOCATION_ADDR = a1.LOCATION_ADDR
    """
    query_db("instance/dtarp.db", query)
    # get_db_schema("instance/dtarp.db")