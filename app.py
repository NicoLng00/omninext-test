from flask import Flask, Blueprint
from mongoengine import connect
from dotenv import load_dotenv
import os
from flask_restx import Api
from flask_jwt_extended import JWTManager
from datetime import timedelta
from Modules.Users.User import User     
from Modules.Users.Controllers.UserController import user_ns
from Modules.Auth.Controllers.AuthController import auth_ns


app = Flask(__name__)

load_dotenv()
connect(host=os.getenv("MONGO_URI"), alias='default')

# JWT Authentication
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

# Swagger UI
api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(
    api_bp,
    version='1.0',
    title='Omninext API',
    description='A set of APIs for Omninext backend services',
    doc='/docs',
    authorizations={
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
        },
    },
    security='Bearer Auth'
)

api.add_namespace(user_ns, path='/users')
api.add_namespace(auth_ns, path='/auth')

app.register_blueprint(api_bp)


if __name__ == "__main__":
    app.run(debug=True)
