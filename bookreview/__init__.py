from flask import Flask
from bookreview.routes import routes
from bookreview.config import BaseConfig


app = Flask(__name__)
app.config.from_object(BaseConfig)
app.register_blueprint(routes)
