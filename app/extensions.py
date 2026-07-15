from flask_cors import CORS
from flask_marshmallow import Marshmallow
from firebase_admin import firestore

cors = CORS()
ma = Marshmallow()

def get_db():
    return firestore.client()
