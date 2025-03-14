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
    
    # Create message placeholder - using a container rather than chat_message
    # to avoid the nested chat message error
    message_container = st.container()
    
    # Create a placeholder for tools that will appear before the message
    tools_container = st.container()
    
    with message_container:
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
    
    # Clear previous messages to avoid duplication
    st.empty()
    
    try:
        # Add user message to chat history
        add_message("user", message)
        
        # Display user message on right side
        with st.chat_message("user"):
            st.markdown(message)
        
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
        
        # Create a container for the assistant response
        with st.chat_message("assistant"):
            # First, create a container for tools that will appear before the message
            if st.session_state.is_processing:
                tool_container = st.container()
            
            # Send the streaming request
            with requests.post(f"{BACKEND_URL}/api/chat", json=payload, stream=True) as response:
                response.raise_for_status()
                
                # Process streaming response
                assistant_message = render_streaming_message(response)
            
            # Now display tools BEFORE content
            from frontend.components.chat_message import (
                render_tools,
                render_sources,
                render_suggested_questions,
            )
            
            # Display tools first
            if assistant_message["tools"]:
                render_tools(assistant_message["tools"])
            
            # Display main content
            st.markdown(assistant_message["content"])
            
            # Display sources
            if assistant_message["sources"]:
                render_sources(assistant_message["sources"])
            
            # Add suggested questions outside the chat message to avoid nesting error
            if assistant_message["suggested_questions"]:
                st.markdown("**Suggested questions:**")
                cols = st.columns(min(3, len(assistant_message["suggested_questions"])))
                for i, (col, question) in enumerate(zip(cols, assistant_message["suggested_questions"])):
                    with col:
                        if st.button(question, key=f"q_{i}", use_container_width=True):
                            # We'll rerun with the question instead of directly calling send_message
                            # to avoid nested messages issue
                            st.session_state.next_question = question
                            st.rerun()
        
        # Add assistant message to chat history
        add_message(
            "assistant",
            assistant_message["content"],
            sources=assistant_message["sources"],
            tools=assistant_message["tools"],
            suggested_questions=assistant_message["suggested_questions"]
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
    # Check if we have a next question from the suggested questions
    if hasattr(st.session_state, 'next_question') and st.session_state.next_question:
        question = st.session_state.next_question
        st.session_state.next_question = None
        send_message(question)
        return
    
    # Render chat history - we'll handle this differently to avoid duplicates
    if not st.session_state.is_processing:
        for i, message in enumerate(get_message_history()):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant"):
                    # Display tools first if present
                    if "tools" in message and message["tools"]:
                        from frontend.components.chat_message import render_tools
                        render_tools(message["tools"])
                    
                    # Display content
                    st.markdown(message["content"])
                    
                    # Display sources if present
                    if "sources" in message and message["sources"]:
                        from frontend.components.chat_message import render_sources
                        render_sources(message["sources"])
                    
                    # Display suggested questions properly
                    if "suggested_questions" in message and message["suggested_questions"]:
                        st.markdown("**Suggested questions:**")
                        cols = st.columns(min(3, len(message["suggested_questions"])))
                        for j, (col, question) in enumerate(zip(cols, message["suggested_questions"])):
                            with col:
                                if st.button(question, key=f"q_{i}_{j}", use_container_width=True):
                                    st.session_state.next_question = question
                                    st.rerun()
    
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
