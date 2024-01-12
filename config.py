import os
from dotenv import load_dotenv


load_dotenv()
# Get the base directory of this folder
basedir = os.path.abspath(os.path.dirname(__file__))
# "C:\\Users\\bstan\\Documents\\codingtemple-kekambas-137\\week6\\flask_api"

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG')