import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import json
import random
import time
from chatbot.chatbot import MentalHealthChatbot  # Import the enhanced chatbot

# Initialize the chatbot
chatbot = MentalHealthChatbot()

# ... [Keep all your database and helper functions the same] ...

def main():
    st.set_page_config(page_title="College Portal", layout="wide")
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Initialize databases
    init_db()
    
    # Login page - shown first
    if not st.session_state.authenticated:
        show_login()
        return
    
    # Main application after login
    st.sidebar.title(f"Welcome, {st.session_state.user['username']}")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()
    
    # Navigation options in your preferred order
    nav_options = ["Outpass Application", "Chatbot"]
    
    # Add admin options if needed
    if st.session_state.user['role'] in ['admin', 'staff']:
        nav_options.append("Outpass Approvals")
    
    # Create navigation radio buttons in sidebar
    selection = st.sidebar.radio("Go to", nav_options)
    
    # Show the selected page
    if selection == "Outpass Application":
        show_outpass()
    elif selection == "Chatbot":
        show_chatbot()
    elif selection == "Outpass Approvals":
        show_outpass_approvals()

def show_login():
    st.title("College Portal Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login"):
            user = authenticate(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = {
                    'id': user[0],
                    'username': user[1],
                    'role': user[3]
                }
                st.rerun()
            else:
                st.error("Invalid username or password")

# ... [Keep all your other page functions the same] ...

def show_chatbot():
    st.title("Mental Health Buddy 🤗")
    st.caption("Your friendly, humorous chatbot here to boost your mood!")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Accept user input
    if prompt := st.chat_input("How are you feeling today?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get chatbot response
        response = chatbot.get_response(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Simulate typing animation
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()