"""
Database initialization script.
Creates all tables per TDD Section 6.
"""

from app import create_app
from app.models.database import Base, engine

def init_db():
    app = create_app()
    with app.app_context():
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_db()
