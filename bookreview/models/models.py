from flask_login import UserMixin
from bookreview import db, login_manager, app
from itsdangerous import URLSafeTimedSerializer, BadSignature


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(24), unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    profile_photo = db.Column(db.Text, default='standard_user_pic.jpg')
    username = db.Column(db.String(24))

    def get_reset_token(self, option):
        s = URLSafeTimedSerializer(app.config["SECRET_KEY"], salt=option)
        return s.dumps({"id": self.id})

    @staticmethod
    def verify_token(token):
        serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        try:
            user_id = serializer.loads(token, max_age=1800)["id"]
            return User.query.get(int(user_id))
        except BadSignature:
            pass

    def __repr__(self):
        return f"User {self.id} | {self.login} | {self.email}"
