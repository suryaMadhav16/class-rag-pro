"""
Chat message component for the Streamlit application.
"""
import streamlit as st
import json
from typing import Dict, List, Optional

def render_tools(tools: List[Dict]):
    """
    Render tool calls in an expandable accordion.
    
    Args:
        tools: List of tool information
    """
    if not tools:
        return
    
    with st.expander("🔧 Tool Calls", expanded=False):
        for i, tool in enumerate(tools):
            if "title" in tool:
                st.subheader(tool["title"])
            
            if "toolCall" in tool and "toolOutput" in tool:
                tool_name = tool.get("toolCall", {}).get("name", f"Tool {i+1}")
                tool_input = tool.get("toolCall", {}).get("input", {})
                tool_output = tool.get("toolOutput", {}).get("output", "")
                is_error = tool.get("toolOutput", {}).get("isError", False)
                
                with st.expander(f"{tool_name}", expanded=False):
                    st.markdown("**Input:**")
                    
                    if isinstance(tool_input, dict) and tool_input:
                        st.json(tool_input)
                    else:
                        st.code(str(tool_input), language="text")
                    
                    st.markdown("**Output:**")
                    
                    if is_error:
                        st.error(str(tool_output))
                    elif isinstance(tool_output, dict):
                        st.json(tool_output)
                    else:
                        st.markdown(str(tool_output))
            else:
                # Fallback for other tool formats
                st.code(json.dumps(tool, indent=2), language="json")

def render_sources(sources: List[Dict]):
    """
    Render sources in an expandable accordion.
    
    Args:
        sources: List of source information
    """
    if not sources:
        return
    
    with st.expander("📚 Sources", expanded=False):
        for i, source in enumerate(sources):
            file_name = source.get("metadata", {}).get("file_name", f"Source {i+1}")
            score = source.get("score", "N/A")
            
            with st.expander(
                f"{file_name} (Score: {score:.2f})" if isinstance(score, float) else f"{file_name} (Score: {score})",
                expanded=False
            ):
                st.markdown(source.get("text", ""))
                
                if source.get("url"):
                    st.markdown(f"[View document]({source['url']})")

def render_suggested_questions(questions: List[str], on_question_click):
    """
    Render suggested follow-up questions.
    
    Args:
        questions: List of question strings
        on_question_click: Callback function when a question is clicked
    """
    if not questions:
        return
    
    st.markdown("**Suggested questions:**")
    
    # Calculate number of columns (max 3)
    num_columns = min(3, len(questions))
    cols = st.columns(num_columns)
    
    for i, (col, question) in enumerate(zip(cols, questions)):
        with col:
            if st.button(question, key=f"q_{i}"):
                on_question_click(question)

def render_chat_message(message: Dict, on_question_click=None):
    """
    Render a single chat message with tools, sources, and suggested questions.
    
    Args:
        message: Message object including content and optional tools, sources, etc.
        on_question_click: Optional callback function when a suggested question is clicked
    """
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        if message["role"] == "assistant":
            # Render tools if present
            if "tools" in message and message["tools"]:
                render_tools(message["tools"])
            
            # Render sources if present
            if "sources" in message and message["sources"]:
                render_sources(message["sources"])
            
            # Render suggested questions if present and callback provided
            if "suggested_questions" in message and message["suggested_questions"] and on_question_click:
                render_suggested_questions(message["suggested_questions"], on_question_click)
