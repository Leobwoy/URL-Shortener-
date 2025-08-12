from app import create_app, db
from app.models import URL

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database initialized successfully!")
    print("Tables created: urls")
