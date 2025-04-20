from logging.config import fileConfig
import os
import sys
import logging
from sqlalchemy import engine_from_config, pool, exc, text, create_engine
from alembic import context

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the database setup and models
from DB.database import Base, DATABASE_URL, DB_TYPE, check_db_connection
from DB.models import User, Conversation, Message, UserSettings, Subscription, Payment

# Set up logger
logger = logging.getLogger("alembic")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# Use the metadata from our SQLAlchemy models
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Use our DATABASE_URL from database.py
    url = DATABASE_URL
    logger.info(f"Configuring offline migration with URL: {url}")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Additional migration options
        compare_type=True,
        compare_server_default=True,
        render_as_batch=DB_TYPE == "sqlite",  # Enable batch migrations for SQLite
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Check database connection before running migrations
    try:
        # Check if we can connect to the database
        if not check_db_connection():
            logger.error("❌ Failed to connect to database. Please check configuration.")
            sys.exit(1)
        
        logger.info(f"✅ Successfully connected to the {DB_TYPE} database")
        # Use our DATABASE_URL directly
        logger.info(f"Using database URL: {DATABASE_URL}")
        
        # Create engine directly with our configuration
        engine_args = {}
        if DB_TYPE == "sqlite":
            engine_args["connect_args"] = {"check_same_thread": False}
        
        # Create engine directly instead of using engine_from_config
        connectable = create_engine(
            DATABASE_URL,
            poolclass=pool.NullPool,
            **engine_args
        )
    except Exception as e:
        logger.error(f"❌ Error configuring database connection: {str(e)}")
        sys.exit(1)

    # Run migrations with the database connection
    try:
        with connectable.connect() as connection:
            # Test connection
            try:
                connection.execute(text("SELECT 1"))
                logger.info("✅ Database connection verified")
            except exc.SQLAlchemyError as e:
                logger.error(f"❌ Database connection failed: {str(e)}")
                sys.exit(1)
                
            context.configure(
                connection=connection, 
                target_metadata=target_metadata,
                # Additional migration options
                compare_type=True,
                compare_server_default=True,
                render_as_batch=DB_TYPE == "sqlite",  # Enable batch migrations for SQLite
            )
            
            with context.begin_transaction():
                context.run_migrations()
    except Exception as e:
        logger.error(f"❌ Error running migrations: {str(e)}")
        sys.exit(1)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
