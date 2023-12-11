from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import psycopg2

# Create a sqlite engine instance
#engine = create_engine("sqlite:///punto.db", max_overflow=-1)
engine = create_engine("postgresql://root:root@localhost:5432/punto_venta", max_overflow=-1)

# Create a DeclarativeMeta instance
Base = declarative_base()