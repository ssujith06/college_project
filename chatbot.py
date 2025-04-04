import json
import random
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

nlp = spacy.load("en_core_web_sm")

class AdvancedChatbot:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.intents = self.load_intents()
        self.setup_nlp()
        self.personality = {
            'tone': 'witty',
            'response_style': 'empathetic',
            'complexity': 0.8
        }
        
    def load_intents(self):
        with open('chatbot/intents.json') as f:
            data = json.load(f)
            # Vectorize all patterns during initialization
            all_patterns = [p for intent in data['intents'] for p in intent['patterns']]
            self.vectorizer.fit(all_patterns)
            return data

    def setup_nlp(self):
        # Load additional resources
        self.special_responses = {
            'stress': [
                "Stress is like a Wi-Fi signal - the closer you are to the source, the stronger it gets! Step back!",
                "Your brain is like a browser with 50 tabs open. Time to close some tabs! 🖥️"
            ],
            'fun_facts': [
                "Did you know? The shortest war was between Britain and Zanzibar (38 minutes)!",
                "Fun fact: Bananas are berries but strawberries aren't! Mind = blown 🤯"
            ]
        }

    def process_input(self, text):
        doc = nlp(text)
        return {
            'entities': [(ent.text, ent.label_) for ent in doc.ents],
            'sentiment': self.analyze_sentiment(doc),
            'keywords': [token.lemma_ for token in doc if not token.is_stop]
        }

    def generate_response(self, user_input):
        # NLP processing
        analysis = self.process_input(user_input)
        
        # Intent classification
        intent = self.classify_intent(user_input)
        
        # Context-aware response generation
        base_response = self.select_response(intent, analysis)
        enhanced = self.enhance_response(base_response, analysis)
        
        return self.format_response(enhanced)

    def classify_intent(self, text):
        vector = self.vectorizer.transform([text])
        max_sim = -1
        best_intent = None
        
        for intent in self.intents['intents']:
            intent_vectors = self.vectorizer.transform(intent['patterns'])
            sim = max(cosine_similarity(vector, intent_vectors)[0])
            if sim > max_sim:
                max_sim = sim
                best_intent = intent['tag']
        
        return best_intent if max_sim > 0.4 else None

    def select_response(self, intent, analysis):
        if not intent:
            return random.choice([
                "I'm still learning, but here's a fun fact for you!",
                *self.special_responses['fun_facts']
            ])
            
        intent_data = next(i for i in self.intents['intents'] if i['tag'] == intent)
        
        # Sentiment-based selection
        if analysis['sentiment'] < -0.5:
            return random.choice(intent_data.get('supportive_responses', intent_data['responses']))
        return random.choice(intent_data['responses'])

    def enhance_response(self, response, analysis):
        enhancements = []
        
        # Add personality
        if self.personality['tone'] == 'witty':
            enhancements.append(" " + random.choice([
                " BTW, you're awesome!",
                " Fun fact: " + random.choice(self.special_responses['fun_facts']),
                " 😄"
            ]))
        
        # Add entity references
        for entity, label in analysis['entities']:
            if label == 'DATE':
                enhancements.append(f" Mark your calendar for {entity}!")
            elif label == 'PERSON':
                enhancements.append(f" Say hi to {entity} for me!")
        
        return response + "".join(enhancements)

    def format_response(self, text):
        # Add typing delay calculation
        words = text.split()
        delay = min(0.1, max(0.03, 1.5/len(words)))
        
        return {
            'text': text,
            'typing_delay': delay
        }
