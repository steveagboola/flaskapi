import os 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# creating an instance
db = SQLAlchemy(app)
migrate = Migrate(app,db)  #this is where it gets the Migrate name to build the folder

from . import routes, models
