import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Define the base class for declarative model
Base = declarative_base()

# User table
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)

    # Relationships
    notes = relationship('Note', back_populates='user')
    favorites = relationship('Favorites', back_populates='user')

# Note table
class Note(Base):
    __tablename__ = 'notes'

    note_id = Column(Integer, primary_key=True)
    data = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    # Relationship with User
    user = relationship('User', back_populates='notes')

# Favorites table (weak entity)
class Favorites(Base):
    __tablename__ = 'favorites'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    reid = Column(Integer, ForeignKey('dtarp.reid'), primary_key=True)

    # Relationships
    user = relationship('User', back_populates='favorites')

# Create a single SQLite database file
database_file = 'realestate.db'  # Specify your desired database filename
engine = create_engine(f'sqlite:///{database_file}', echo=True)

# Create all tables
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Close the session
session.close()
