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
        layout="wide",
        # Set default to dark theme
        initial_sidebar_state="expanded"
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
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    
    /* Style user messages to be on the right */
    .stChatMessage[data-testid="user-message"] {
        background-color: #0084ff !important;
        border-bottom-right-radius: 0 !important;
        margin-left: 20% !important;
    }
    
    /* Style assistant messages to be on the left */
    .stChatMessage[data-testid="assistant-message"] {
        background-color: #383838 !important;
        border-bottom-left-radius: 0 !important;
        margin-right: 20% !important;
    }
    
    /* Improve button styling for suggested questions */
    .stButton button {
        border-radius: 20px;
        padding: 2px 15px;
        font-size: 0.9em;
        border: 1px solid rgba(128, 128, 128, 0.4);
        background-color: rgba(128, 128, 128, 0.1);
    }
    
    /* Add some padding to expanders */
    .streamlit-expanderHeader {
        font-size: 1em;
        font-weight: 600;
    }
    
    /* Improve tool styling */
    .streamlit-expanderContent {
        padding: 0.5rem;
        background-color: rgba(128, 128, 128, 0.05);
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
