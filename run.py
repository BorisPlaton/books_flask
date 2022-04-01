from bookreview import create_app
from bookreview.config import DevConfig

app = create_app(DevConfig)

if __name__ == "__main__":
    app.run()
