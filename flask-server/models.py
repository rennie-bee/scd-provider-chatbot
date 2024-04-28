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

    def save(self, table):
        item = {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'medical_id': self.medical_id,
            'preferred_name': self.preferred_name,
            'user_image': self.user_image,
            'expertise': self.expertise
        }
        table.put_item(Item=item)

    @classmethod
    def get(cls, user_id, table):
        response = table.get_item(
            Key={
                'user_id': user_id
            }
        )
        if 'Item' in response:
            return cls(**response['Item'])
        else:
            return None

    def __repr__(self):
        return f'<UserProfile {self.user_id}>'
