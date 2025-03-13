from flask import Flask, Blueprint
from mongoengine import connect
from dotenv import load_dotenv
import os
from flask_restx import Api
from Modules.Users.User import User     
from Modules.Users.Controllers.UserController import user_ns


app = Flask(__name__)

load_dotenv()
connect(host=os.getenv("MONGO_URI"), alias='default')

# Swagger UI
api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(
    api_bp,
    version='1.0',
    title='OmniText API',
    description='A set of APIs for OmniText backend services',
    doc='/docs',
)

api.add_namespace(user_ns, path='/users')

app.register_blueprint(api_bp)


if __name__ == "__main__":
    app.run(debug=True)
