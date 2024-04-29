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

from datetime import datetime, timezone

class ChatSession:
    def __init__(self, user_id, session_id, start_time, end_time=None):
        self.user_id = user_id
        self.session_id = session_id
        # Ensure timestamps are string formatted
        self.start_time = start_time if isinstance(start_time, str) else start_time.isoformat()
        self.end_time = end_time if isinstance(end_time, str) or end_time is None else end_time.isoformat()

    def save(self, table):
        item = {
            'user_id': self.user_id,
            'session_id': self.session_id,
            'start_time': self.start_time,
            'end_time': self.end_time
        }
        table.put_item(Item=item)

    @classmethod
    def get(cls, user_id, session_id, table):
        response = table.get_item(
            Key={
                'user_id': user_id,
                'session_id': session_id
            }
        )
        if 'Item' in response:
            return cls(**response['Item'])
        else:
            return None

    def __repr__(self):
        return f'<ChatSession {self.user_id} {self.session_id}>'


class ChatMessage:
    def __init__(self, user_id, session_id, user_input, user_input_timestamp, chatbot_response, chatbot_response_timestamp):
        self.user_id = user_id
        self.session_id = session_id
        self.user_input = user_input
        self.chatbot_response = chatbot_response
        # Ensure timestamps are string formatted
        self.user_input_timestamp = user_input_timestamp if isinstance(user_input_timestamp, str) else user_input_timestamp.isoformat()
        self.chatbot_response_timestamp = chatbot_response_timestamp if isinstance(chatbot_response_timestamp, str) else chatbot_response_timestamp.isoformat()
        # Creating a composite sort key
        self.session_id_timestamp = f"{session_id}#{self.user_input_timestamp}"

    def save(self, table):
        item = {
            'user_id': self.user_id,
            'session_id_timestamp': self.session_id_timestamp,
            'user_input': self.user_input,
            'user_input_timestamp': self.user_input_timestamp,
            'chatbot_response': self.chatbot_response,
            'chatbot_response_timestamp': self.chatbot_response_timestamp
        }
        table.put_item(Item=item)

    @classmethod
    def get(cls, user_id, session_id_timestamp, table):
        response = table.get_item(
            Key={
                'user_id': user_id,
                'session_id_timestamp': session_id_timestamp
            }
        )
        if 'Item' in response:
            # Split session_id_timestamp to reconstruct original session_id and timestamps
            session_id, user_input_timestamp = response['Item']['session_id_timestamp'].split('#')
            return cls(user_id, session_id, response['Item']['user_input'], user_input_timestamp, response['Item']['chatbot_response'], response['Item']['chatbot_response_timestamp'])
        else:
            return None

    def __repr__(self):
        return f'<ChatMessage {self.user_id} {self.session_id} {self.user_input_timestamp} {self.user_input} {self.chatbot_response}>'


