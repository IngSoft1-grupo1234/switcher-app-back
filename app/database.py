
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.session import sessionmaker


# Crea archivo.sqlite en el path del proyecto
sqlite_file_name = "database.sqlite"
base_dir = os.path.dirname(os.path.realpath(__file__))
database_url = f"sqlite:///{os.path.join(base_dir, sqlite_file_name)}"

engine = create_engine(database_url, echo=False)

Base = declarative_base()

# Crea la tabla
Base.metadata.create_all(engine)

# Crea la sesion
session = sessionmaker(bind=engine)