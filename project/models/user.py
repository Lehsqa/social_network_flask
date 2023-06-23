from .extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    last_login = db.Column(db.DateTime)
    last_request = db.Column(db.DateTime)

    def __repr__(self):
        return {
            'id': self.id,
            'username': self.username,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_request': self.last_request.isoformat() if self.last_request else None
        }
