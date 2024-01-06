from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary


app = Flask(__name__)
app.secret_key = 'àgkdsjalgnjksdgjksdgsdgjksdgkjlskjldgkjl'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:1234@localhost/flightdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 2
app.config["COMMENT_SIZE"] = 1


db = SQLAlchemy(app)
login = LoginManager(app=app)

cloudinary.config(
    cloud_name='de4ynzwro',
    api_key='163145164337242',
    api_secret='JvB-DxVjDyEpPEHXcjZvBMVJYR0',
)



