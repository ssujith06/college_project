import json
import random
import streamlit as st
from datetime import datetime

class MentalHealthChatbot:
    def __init__(self):
        self.intents = self.load_intents()
        self.mood_responses = {
            'stressed': [
                "I see you're stressed. Remember, even diamonds are created under pressure!",
                "Stress is just your brain's way of saying 'This is important!' Take a deep breath.",
                "When stressed, think of yourself as a teabag - you don't know your strength until you're in hot water!"
            ],
            'tired': [
                "Tired? That's just your body's way of saying 'I did great today!'",
                "Even superheroes need naps. Take a break!",
                "Being tired means you're productive. Or you stayed up watching cat videos. Both are valid."
            ],
            'overwhelmed': [
                "Feeling overwhelmed? How do you eat an elephant? One bite at a time!",
                "You're not alone in this. Even Gandalf needed the Fellowship!",
                "Overwhelmed is just a temporary state. Like being hungry. Or needing to pee."
            ],
            'happy': [
                "Yay! Happiness detected! Quick, do a little dance!",
                "Someone's happy! Is it your birthday? Or did you find pizza in the fridge?",
                "Happiness looks good on you! Keep shining!"
            ]
        }
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them!",
            "Why don't skeletons fight each other? They don't have the guts!",
            "I'm reading a book about anti-gravity. It's impossible to put down!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!"
        ]
        self.encouragements = [
            "You're doing amazing! Remember, even baby steps move you forward.",
            "The fact that you're here means you care - that's already winning!",
            "You're like a smartphone - way more capable than you think you are!",
            "Remember: You survived 100% of your bad days so far. That's a perfect record!"
        ]

    def load_intents(self):
        with open('chatbot/intents.json') as file:
            return json.load(file)

    def detect_mood(self, message):
        message = message.lower()
        mood_keywords = {
            'stressed': ['stress', 'pressure', 'anxious', 'nervous'],
            'tired': ['tired', 'exhausted', 'sleepy', 'fatigue'],
            'overwhelmed': ['overwhelm', 'too much', 'can\'t handle', 'drowning'],
            'happy': ['happy', 'great', 'awesome', 'amazing', 'good']
        }
        
        for mood, keywords in mood_keywords.items():
            if any(keyword in message for keyword in keywords):
                return mood
        return None

    def get_response(self, message):
        message = message.lower()
        mood = self.detect_mood(message)
        
        # Special responses for time-based greetings
        current_hour = datetime.now().hour
        if any(greeting in message for greeting in ['hi', 'hello', 'hey']):
            if 5 <= current_hour < 12:
                return random.choice([
                    "Good morning sunshine! Ready to conquer the day? ☀️",
                    "Top of the morning to you! May your coffee be strong and your lectures short!"
                ])
            elif 12 <= current_hour < 17:
                return random.choice([
                    "Good afternoon! How's your day treating you so far?",
                    "Afternoon alert! Half the day is done - you're crushing it!"
                ])
            elif 17 <= current_hour < 22:
                return random.choice([
                    "Good evening! Time to relax and recharge! 🌙",
                    "Evening greetings! Did you know otters hold hands while sleeping? You should find someone to hold hands with too!"
                ])
            else:
                return random.choice([
                    "Hello night owl! Burning the midnight oil?",
                    "Up late? Remember, even Batman sleeps sometimes!"
                ])
        
        # Mood-specific responses
        if mood:
            return random.choice(self.mood_responses[mood])
        
        # Jokes
        if any(trigger in message for trigger in ['joke', 'funny', 'laugh']):
            return random.choice(self.jokes)
        
        # Encouragement
        if any(trigger in message for trigger in ['sad', 'depressed', 'down', 'bad day']):
            return random.choice(self.encouragements + [
                "Bad days are just the universe's way of making the good ones feel extra good!",
                "You know what's great about hitting rock bottom? There's only one way to go from here - up!",
                "When life gives you lemons, squirt life in the eye and run away laughing!"
            ])
        
        # Study motivation
        if any(trigger in message for trigger in ['study', 'exam', 'test', 'assignment']):
            return random.choice([
                "Remember: You don't have to be perfect, just better than you were yesterday!",
                "Studying is like eating an elephant - one bite at a time! (Please don't actually eat elephants)",
                "The expert in anything was once a beginner. Keep going!"
            ])
        
        # Default intent matching
        for intent in self.intents['intents']:
            for pattern in intent['patterns']:
                if pattern.lower() in message:
                    return random.choice(intent['responses'])
        
        # Fallback responses with humor
        return random.choice([
            "I'm not sure I understand, but here's a fun fact: Cows have best friends!",
            "I'm still learning. Did you know the shortest war in history was between Britain and Zanzibar in 1896? It lasted 38 minutes!",
            "I might be a bot, but I know one thing for sure - you're awesome!",
            "I didn't get that, but here's a joke to cheer you up: " + random.choice(self.jokes)
        ])