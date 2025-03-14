"""
Main Streamlit application file.
"""
import streamlit as st

from frontend.config import APP_TITLE, APP_ICON, APP_DESCRIPTION
from frontend.utils.session import initialize_session_state
from frontend.utils.api import get_chat_config
from frontend.components.sidebar import render_sidebar
from frontend.components.chat_interface import render_chat_interface, render_starter_questions

def main():
    """
    Main application function.
    """
    # Configure page
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Fetch chat configuration if not already available
    if not st.session_state.chat_config:
        st.session_state.chat_config = get_chat_config()
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.markdown(APP_DESCRIPTION)
    
    # Render starter questions if no messages
    render_starter_questions()
    
    # Render chat interface
    render_chat_interface()
    
    # Add custom CSS for better styling
    st.markdown("""
    <style>
    /* Hide Streamlit branding */
    #MainMenu, footer {visibility: hidden;}
    
    /* Improve chat message styling */
    .stChatMessage {
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Make chat input more prominent */
    .stChatInputContainer {
        padding: 0.5rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
