from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_uploads import UploadSet, IMAGES, configure_uploads
from bookreview.config import BaseConfig

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
profile_img = UploadSet("profileimg", IMAGES)
configure_uploads(app, profile_img)

from bookreview.models.models import load_user
from bookreview.routes import authorization, main

app.register_blueprint(authorization)
app.register_blueprint(main)
