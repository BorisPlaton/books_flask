from flask import Flask
from bookreview.routes import routes


app = Flask(__name__)

app.register_blueprint(routes)
