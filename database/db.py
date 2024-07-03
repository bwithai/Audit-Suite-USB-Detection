import os

from sqlmodel import SQLModel, create_engine, Session
import utils

# Create DB Engine and Session
engine = create_engine(utils.get_database_url(), echo=False)
SessionLocal = Session(engine)


def archive_db(path: str = ""):
    db_path = os.path.join(path)  # db_path = os.path.join("C:\\Windows\\System32")
    if os.path.isfile(path):
        url = f"sqlite:///{db_path}"
    else:
        db_name = "archive.sqlite"
        url = f"sqlite:///{db_path}\\{db_name}"

    if path == "":
        return None
    else:
        archive_engine = create_engine(url, echo=False)

        # Create tables in the archive database if they don't exist
        SQLModel.metadata.create_all(archive_engine)

        return Session(archive_engine)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Dependency
def get_db_dependency():
    db = SessionLocal
    try:
        yield db
    finally:
        db.close()


# Dependency
def get_db():
    return SessionLocal
