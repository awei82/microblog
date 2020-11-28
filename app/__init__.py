from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app, engine_options={'connect_args':{'check_same_thread': False}})
migrate = Migrate(app, db)


from app import routes, models
