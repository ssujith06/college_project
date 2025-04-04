import streamlit as st
from chatbot.chatbot import AdvancedChatbot
import time

# Custom CSS injection
def inject_custom_ui():
    st.markdown("""
    <style>
        .stChatInput { border-radius: 20px !important; }
        .stChatMessage { 
            border-radius: 15px !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 1.2rem !important;
        }
        [data-testid="stChatMessage"] > div:first-child {
            font-size: 1.1em !important;
        }
        .st-emotion-cache-4oy321 {
            gap: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

def show_chatbot():
    st.title("🤖 Campus AI Companion")
    inject_custom_ui()
    
    # Initialize with personality quiz
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = AdvancedChatbot()
        st.session_state.messages = [{
            "role": "assistant", 
            "content": "Hi there! I'm your AI campus buddy. I can:\n"
                      "- Help with academic stress 📚\n"
                      "- Tell dad jokes (the good kind) 😄\n"
                      "- Be your personal cheerleader 🎉\n\n"
                      "What's on your mind today?"
        }]

    # Display messages with avatars
    for msg in st.session_state.messages:
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Chat input with enhanced processing
    if prompt := st.chat_input("Message Campus Buddy..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Generate and display response
        with st.chat_message("assistant", avatar="🤖"):
            response_placeholder = st.empty()
            response = st.session_state.chatbot.generate_response(prompt)
            
            # Typewriter effect with dynamic speed
            full_response = ""
            for chunk in response['text'].split():
                full_response += chunk + " "
                time.sleep(response['typing_delay'])
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response['text']
        })

# [Keep all other functions unchanged]
