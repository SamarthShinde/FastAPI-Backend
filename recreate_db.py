from sqlalchemy import create_engine
from models import Base  # Ensure your models file defines Base (e.g., Base = declarative_base())
import os
import config

# Use your provided PostgreSQL connection string:
DATABASE_URL = config.DATABASE_URL

# Create the engine. For PostgreSQL, no extra connect_args are needed.
engine = create_engine(DATABASE_URL)

# Drop all tables
print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)

# Recreate all tables
print("Creating all tables...")
Base.metadata.create_all(bind=engine)

print("Database has been recreated successfully.")