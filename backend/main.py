from db import engine, Base, SessionLocal
import models


def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")

if __name__ == "__main__":
    init_db()