from mongoengine import Document, StringField, EmailField

class User(Document):
    meta = {'collection': 'users'}
    name = StringField(required=True)
    email = EmailField(required=True, unique=True)


