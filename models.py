from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BookSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    author = db.Column(db.String(256))
    summary = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(512))
