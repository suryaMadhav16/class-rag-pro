"""
Chat interface component for the Streamlit application.
"""
import streamlit as st
import requests
import json
from typing import List, Dict, Any, Callable

from frontend.config import BACKEND_URL
from frontend.utils.api import process_streaming_line
from frontend.utils.session import add_message, get_message_history, start_processing, end_processing
from frontend.components.chat_message import render_chat_message

def render_chat_history(on_question_click: Callable[[str], None]):
    """
    Render the chat history.
    
    Args:
        on_question_click: Callback function when a suggested question is clicked
    """
    # Display chat history
    for message in get_message_history():
        render_chat_message(message, on_question_click)

def render_streaming_message(response) -> Dict:
    """
    Render streaming message from the backend.
    
    Args:
        response: Streaming response object
        
    Returns:
        Dict: Complete message after streaming
    """
    # Variables to collect data from streaming response
    tools = []
    sources = []
    suggested_questions = []
    content = ""
    
    # Create message placeholder
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Process the streaming response line by line
        for line in response.iter_lines():
            if not line:
                continue
                
            line = line.decode('utf-8')
            processed = process_streaming_line(line)
            
            if processed["type"] == "text":
                content += processed["data"]
                # Update display with current content
                message_placeholder.markdown(content)
                
            elif processed["type"] == "data" and processed["data"]:
                data = processed["data"]
                data_type = data.get("type")
                
                if data_type == "events":
                    tools.append(data.get("data", {}))
                    
                elif data_type == "sources":
                    sources = data.get("data", {}).get("nodes", [])
                    
                elif data_type == "suggested_questions":
                    suggested_questions = data.get("data", [])
                    
                elif data_type == "tools":
                    tools.append(data.get("data", {}))
                    
            elif processed["type"] == "error":
                content = f"Error: {processed['data']}"
                message_placeholder.markdown(content)
    
    # Return the complete message
    return {
        "role": "assistant",
        "content": content,
        "sources": sources,
        "tools": tools,
        "suggested_questions": suggested_questions
    }

def send_message(message: str):
    """
    Send a message to the backend and process the response.
    
    Args:
        message: User message
    """
    # Mark processing as started
    start_processing()
    
    try:
        # Add user message to chat history
        add_message("user", message)
        
        # Prepare the payload
        payload = {
            "messages": [
                {"role": msg["role"], "content": msg["content"]}
                for msg in get_message_history()
            ]
        }
        
        # Add file annotations if any
        if st.session_state.files:
            payload["messages"][-1]["annotations"] = [{
                "type": "document_file",
                "data": {"files": st.session_state.files}
            }]
            
            # Clear files after sending
            st.session_state.files = []
        
        # Send the streaming request
        with requests.post(f"{BACKEND_URL}/api/chat", json=payload, stream=True) as response:
            response.raise_for_status()
            
            # Process streaming response
            assistant_message = render_streaming_message(response)
            
            # Add assistant message to chat history
            add_message(
                "assistant",
                assistant_message["content"],
                sources=assistant_message["sources"],
                tools=assistant_message["tools"],
                suggested_questions=assistant_message["suggested_questions"]
            )
            
            # Re-render the last message to include expandable details properly
            with st.chat_message("assistant"):
                st.markdown(assistant_message["content"])
                
                # Import here to avoid circular import
                from frontend.components.chat_message import (
                    render_tools,
                    render_sources,
                    render_suggested_questions,
                )
                
                render_tools(assistant_message["tools"])
                render_sources(assistant_message["sources"])
                
                if assistant_message["suggested_questions"]:
                    render_suggested_questions(
                        assistant_message["suggested_questions"],
                        lambda q: send_message(q)
                    )
    
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")
        
        # Add error message to chat history
        add_message("assistant", f"Error: {str(e)}")
    
    finally:
        # Mark processing as ended
        end_processing()

def render_chat_interface():
    """
    Render the chat interface with history and input.
    """
    # Render chat history
    render_chat_history(send_message)
    
    # Render chat input
    if prompt := st.chat_input("Type your message here...", disabled=st.session_state.is_processing):
        send_message(prompt)

def render_starter_questions():
    """
    Render starter questions if chat history is empty.
    """
    if st.session_state.chat_config.get("starterQuestions") and not st.session_state.messages:
        st.markdown("### Get started by asking:")
        
        cols = st.columns(min(3, len(st.session_state.chat_config["starterQuestions"])))
        
        for i, (col, question) in enumerate(zip(cols, st.session_state.chat_config["starterQuestions"])):
            with col:
                if st.button(question, key=f"starter_{i}"):
                    send_message(question)
