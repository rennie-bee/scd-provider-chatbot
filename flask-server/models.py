from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserProfile(db.Model):
    user_id = db.Column(db.String(128), primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    medical_id = db.Column(db.String(128), nullable=True)
    preferred_name = db.Column(db.String(128), nullable=True)
    email = db.Column(db.String(128), nullable=False)
    user_image = db.Column(db.String(256), nullable=True)  # URL to the image stored in S3
    expertise = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return f'<UserProfile {self.uid}>'