import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Configuration
cred = credentials.Certificate("scd-chatbot-firebase-adminsdk-3zz2o-9a7301481c.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

class UserProfile:
    def __init__(self, user_id, first_name, last_name, email, medical_id=None, preferred_name=None, user_image=None, expertise=None):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.medical_id = medical_id
        self.preferred_name = preferred_name
        self.user_image = user_image
        self.expertise = expertise

    def save(self):
        user_ref = db.collection('users').document(self.user_id)
        user_ref.set(vars(self), merge=True)

    @staticmethod
    def get(user_id):
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        if user_doc.exists:
            return UserProfile(**user_doc.to_dict())
        else:
            return None

    def __repr__(self):
        return f'<UserProfile {self.user_id}>'