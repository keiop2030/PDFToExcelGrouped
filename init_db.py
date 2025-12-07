"""Database initialization script."""
from app import app, db

def init_database():
    """Initialize the database with all tables."""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully!")
        print("✓ Database initialized at: app.db")
        print("\nYou can now run the application with: python app.py")

if __name__ == '__main__':
    init_database()
