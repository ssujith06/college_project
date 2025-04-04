import json
import random
from datetime import datetime

class AdvancedChatbot:
    def __init__(self):
        self.intents = self.load_intents()
        self.personality = {
            'tone': 'witty',
            'response_style': 'empathetic'
        }
        
    def load_intents(self):
        with open('chatbot/intents.json') as f:
            return json.load(f)
    
    def get_response(self, message):
        message = message.lower()
        
        # Simple intent matching (temporary)
        for intent in self.intents['intents']:
            for pattern in intent['patterns']:
                if pattern.lower() in message:
                    response = random.choice(intent['responses'])
                    return self._enhance_response(response)
        
        # Fallback with personality
        return self._enhance_response("I'm still learning! Here's a fun fact: Cows have best friends!")

    def _enhance_response(self, response):
        if self.personality['tone'] == 'witty':
            enhancements = [
                " 😄",
                " You're awesome!",
                " BTW, did you smile today?"
            ]
            return response + random.choice(enhancements)
        return response
