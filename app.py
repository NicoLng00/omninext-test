from flask import Flask
from mongoengine import connect
from dotenv import load_dotenv
import os
from Modules.Users.User import User     
from Modules.Users.Controllers.UserController import user_blueprint


app = Flask(__name__)

load_dotenv()
connect(host=os.getenv("MONGO_URI"), alias='default')

app.register_blueprint(user_blueprint, url_prefix='/api/users')


if __name__ == "__main__":
    app.run(debug=True)
