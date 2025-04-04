import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import json
import random
import time
import os

# Initialize directories
os.makedirs("data", exist_ok=True)
os.makedirs("chatbot", exist_ok=True)

# ====================== CHATBOT IMPLEMENTATION ======================
class MentalHealthChatbot:
    def __init__(self):
        self.intents = self.load_intents()
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them!"
        ]
        self.encouragements = [
            "You're doing great! Remember progress takes time.",
            "Every expert was once a beginner. Keep going!"
        ]

    def load_intents(self):
        try:
            with open('chatbot/intents.json') as file:
                return json.load(file)
        except:
            return {"intents": []}

    def get_response(self, message):
        message = message.lower()
        
        # Special responses
        if any(word in message for word in ['joke', 'funny']):
            return random.choice(self.jokes)
        if any(word in message for word in ['sad', 'depressed']):
            return random.choice(self.encouragements)
        
        # Intent matching
        for intent in self.intents.get('intents', []):
            if any(pattern.lower() in message for pattern in intent['patterns']):
                return random.choice(intent['responses'])
        
        return "I'm still learning! Could you ask differently?"

# ====================== DATABASE FUNCTIONS ======================
def init_db():
    # Users database
    conn = sqlite3.connect('data/credentials.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE,
                 password TEXT,
                 role TEXT)''')
    
    # Sample users
    sample_users = [
        ('admin', hash_password('admin123'), 'admin'),
        ('student1', hash_password('student123'), 'student'),
        ('staff1', hash_password('staff123'), 'staff')
    ]
    
    for user in sample_users:
        try:
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", user)
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()
    
    # Outpass database
    conn = sqlite3.connect('data/outpass.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS outpasses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 student_id INTEGER,
                 reason TEXT,
                 departure DATETIME,
                 return_dt DATETIME,
                 status TEXT DEFAULT 'pending',
                 approved_by TEXT)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    conn = sqlite3.connect('data/credentials.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def create_outpass(student_id, reason, departure, return_dt):
    conn = sqlite3.connect('data/outpass.db')
    c = conn.cursor()
    c.execute("INSERT INTO outpasses (student_id, reason, departure, return_dt) VALUES (?, ?, ?, ?)",
              (student_id, reason, departure, return_dt))
    conn.commit()
    conn.close()

def get_outpasses(user_id, role):
    conn = sqlite3.connect('data/outpass.db')
    c = conn.cursor()
    if role == 'student':
        c.execute("SELECT * FROM outpasses WHERE student_id = ?", (user_id,))
    else:
        c.execute("SELECT * FROM outpasses")
    outpasses = c.fetchall()
    conn.close()
    return outpasses

def update_outpass_status(outpass_id, status, approved_by):
    conn = sqlite3.connect('data/outpass.db')
    c = conn.cursor()
    c.execute("UPDATE outpasses SET status = ?, approved_by = ? WHERE id = ?",
              (status, approved_by, outpass_id))
    conn.commit()
    conn.close()

# ====================== PAGE COMPONENTS ======================
def show_login():
    st.title("College Portal Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login"):
            user = authenticate(username, password)
            if user:
                st.session_state.user = {
                    'id': user[0],
                    'username': user[1],
                    'role': user[3]
                }
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")

def show_outpass():
    st.title("Outpass Application")
    if st.session_state.user['role'] == 'student':
        with st.form("outpass_form"):
            reason = st.text_area("Reason for Outpass")
            col1, col2 = st.columns(2)
            with col1:
                departure = st.date_input("Departure Date")
            with col2:
                return_dt = st.date_input("Return Date")
            
            if st.form_submit_button("Submit Outpass"):
                if return_dt <= departure:
                    st.error("Return date must be after departure date")
                else:
                    create_outpass(
                        st.session_state.user['id'],
                        reason,
                        departure.strftime('%Y-%m-%d'),
                        return_dt.strftime('%Y-%m-%d')
                    )
                    st.success("Outpass submitted successfully!")
        
        st.divider()
        st.subheader("Your Outpass History")
        outpasses = get_outpasses(st.session_state.user['id'], 'student')
        if outpasses:
            for op in outpasses:
                status_color = "green" if op[5] == 'approved' else "orange" if op[5] == 'pending' else "red"
                st.markdown(f"""
                **Outpass ID:** {op[0]}  
                **Reason:** {op[2]}  
                **Status:** <span style="color:{status_color}">{op[5].capitalize()}</span>
                """, unsafe_allow_html=True)
                st.divider()
        else:
            st.info("No outpass applications found")
    else:
        st.warning("Only students can apply for outpasses")

def show_chatbot():
    st.title("Student Support Chatbot")
    st.caption("Ask me anything about college life!")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Type your question here..."):
        bot = MentalHealthChatbot()
        
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display bot response
        response = bot.get_response(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Simulate typing
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})

def show_approvals():
    st.title("Outpass Approvals")
    if st.session_state.user['role'] not in ['staff', 'admin']:
        st.error("Access denied")
        return
    
    outpasses = get_outpasses(None, 'staff')
    if not outpasses:
        st.info("No outpasses pending approval")
        return
    
    for op in outpasses:
        with st.expander(f"Outpass #{op[0]} (Status: {op[5]})"):
            st.write(f"**Student ID:** {op[1]}")
            st.write(f"**Reason:** {op[2]}")
            st.write(f"**Departure:** {op[3]}")
            st.write(f"**Return:** {op[4]}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Approve", key=f"approve_{op[0]}"):
                    update_outpass_status(op[0], 'approved', st.session_state.user['username'])
                    st.rerun()
            with col2:
                if st.button(f"Reject", key=f"reject_{op[0]}"):
                    update_outpass_status(op[0], 'rejected', st.session_state.user['username'])
                    st.rerun()

# ====================== MAIN APP LAYOUT ======================
def main():
    st.set_page_config(
        page_title="College Portal",
        page_icon="🏫",
        layout="wide"
    )
    init_db()
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Show login if not authenticated
    if not st.session_state.authenticated:
        show_login()
        return
    
    # Main app after login
    st.sidebar.title(f"Welcome, {st.session_state.user['username']}")
    st.sidebar.write(f"Role: {st.session_state.user['role'].capitalize()}")
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.pop('user', None)
        st.rerun()
    
    # Navigation options in specified order
    nav_options = ["Outpass Application", "Support Chatbot"]
    if st.session_state.user['role'] in ['staff', 'admin']:
        nav_options.append("Approvals")
    
    # Show selected page
    page = st.sidebar.radio("Navigation", nav_options)
    
    if page == "Outpass Application":
        show_outpass()
    elif page == "Support Chatbot":
        show_chatbot()
    elif page == "Approvals":
        show_approvals()

if __name__ == "__main__":
    main()
