from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from bookreview.config import BaseConfig

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)
login_manager = LoginManager(app)

from bookreview.models.models import load_user
from bookreview.routes.routes import routes
app.register_blueprint(routes)
