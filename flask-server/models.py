class UserProfile:
    def __init__(self, user_id, email, user_name=None, medical_id=None, preferred_name=None, user_image=None, expertise=None):
        self.user_id = user_id
        self.email = email
        self.user_name = user_name
        self.medical_id = medical_id
        self.preferred_name = preferred_name
        self.user_image = user_image
        self.expertise = expertise

    def save(self, table):
        item = {
            'user_id': self.user_id,
            'email': self.email,
            'user_name': self.user_name,
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
        
    @classmethod
    def delete(cls, user_id, session_id, table):
        try:
            response = table.delete_item(
                Key={
                    'user_id': user_id,
                    'session_id': session_id
                }
            )
            return response
        except Exception as e:
            print(f"Error deleting session: {e}")
            return None

    def __repr__(self):
        return f'<ChatSession {self.user_id} {self.session_id}>'

class ChatMessage:
    def __init__(self, user_id, session_id, message_id, timestamp, user_input, user_input_timestamp, chatbot_response, chatbot_response_timestamp):
        # Creating a composite partition key
        self.user_session_id = f"{user_id}#{session_id}"
        self.message_id = message_id
        # Timestamp as sort key
        self.timestamp = timestamp if isinstance(timestamp, str) else timestamp.isoformat()
        self.user_input = user_input
        self.chatbot_response = chatbot_response
        # Ensure timestamps are string formatted
        self.user_input_timestamp = user_input_timestamp
        self.chatbot_response_timestamp = chatbot_response_timestamp

    def save(self, table):
        item = {
            'user_session_id': self.user_session_id,
            'message_id': self.message_id,
            'timestamp': self.timestamp,
            'user_input': self.user_input,
            'user_input_timestamp': self.user_input_timestamp,
            'chatbot_response': self.chatbot_response,
            'chatbot_response_timestamp': self.chatbot_response_timestamp
        }
        table.put_item(Item=item)

    @classmethod
    def get(cls, user_session_id, message_id, table):
        response = table.get_item(
            Key={
                'user_session_id': user_session_id,
                'message_id': message_id
            }
        )
        if 'Item' in response:
            # Split session_id_timestamp to reconstruct original session_id and timestamps
            user_id, session_id = response['Item']['user_session_id'].split('#')
            return cls(user_id, session_id, response['Item']['message_id'], response['Item']['timestamp'], response['Item']['user_input'], response['Item']['user_input_timestamp'], response['Item']['chatbot_response'], response['Item']['chatbot_response_timestamp'])
        else:
            return None
    
    @classmethod
    def delete(cls, user_session_id, message_id, table):
        try:
            response = table.delete_item(
                Key={
                    'user_session_id': user_session_id,
                    'message_id': message_id
                }
            )
            return response
        except Exception as e:
            print(f"Error deleting message: {e}")
            return None

    def __repr__(self):
        return f'<ChatMessage {self.user_session_id} {self.message_id} {self.timestamp} {self.user_input} {self.chatbot_response}>'


