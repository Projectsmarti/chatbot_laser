import os
import google.generativeai as genai
import streamlit as st
from PIL import Image
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google Generative AI (Gemini) API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'support_stage' not in st.session_state:
    st.session_state.support_stage = "welcome"

# Predefined welcome message
WELCOME_MESSAGE = "Welcome to LaserTech Support Assistant! How can I assist you today?"


# Load company logo
def load_logo():
    return Image.open("logo.jpeg")


def get_enhanced_prompt(user_input, context=None):
    """Generate enhanced prompts for better responses"""
    base_prompt = f"""
    You are an expert laser manufacturing support specialist. 
    Context: {context if context else 'Initial inquiry'}

    Key Guidelines:
    1. Provide specific, actionable solutions
    2. Include safety considerations
    3. Mention when escalation to technical support is needed
    4. Ask for clarification if needed

    User Input: {user_input}

    Respond in a clear, structured manner with:
    1. Issue identification
    2. Immediate steps to take
    3. Preventive measures
    4. Safety warnings if applicable
    """
    return base_prompt


def get_gemini_response(prompt, context=None):
    """Get enhanced response from Google Gemini model"""
    try:
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config
        )

        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [prompt],
                }
            ]
        )

        response = chat_session.send_message(prompt)
        return response.text
    except Exception as exc:
        print(f"Error generating response: {exc}")
        return "An error occurred while generating a response. Please try again."


def main():
    # Custom CSS for centering and styling
    st.markdown("""
        <style>
            .main > div {
                max-width: 800px;
                margin: 0 auto;
                padding: 1rem;
            }
            .logo-container {
                text-align: center;
                margin-bottom: 2rem;
            }
            .logo-container img {
                width: 200px;
                height: auto;
                margin: 0 auto;
            }
            .stButton > button {
                display: block;
                margin: 1rem auto;
                width: 200px;
            }
            .chat-message {
                margin: 1rem 0;
                padding: 1rem;
                border-radius: 10px;
            }
            .user-message {
                background-color: #e3f2fd;
                margin-left: 20%;
            }
            .assistant-message {
                background-color: #f5f5f5;
                margin-right: 20%;
            }
        </style>
    """, unsafe_allow_html=True)

    # Center-aligned logo
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image(load_logo(), width=200)
    st.markdown('</div>', unsafe_allow_html=True)

    # Centered title
    st.markdown('<h1 style="text-align: center;">LaserTech Support Assistant</h1>', unsafe_allow_html=True)

    # Welcome stage
    if st.session_state.support_stage == "welcome":
        st.markdown(f'<p style="text-align: center;">{WELCOME_MESSAGE}</p>', unsafe_allow_html=True)
        st.session_state.chat_history = []

        # Centered start button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Start Support Session"):
                st.session_state.support_stage = "support"
                st.experimental_rerun()

    # Support stage
    elif st.session_state.support_stage == "support":
        # Centered chat container
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(
                    f'<div class="chat-message user-message">👤 <strong>You:</strong> {message["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-message assistant-message">🤖 <strong>Assistant:</strong> {message["content"]}</div>',
                    unsafe_allow_html=True
                )

        # Centered input box
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            user_input = st.text_area("", placeholder="Type your message here...", height=100)

            # Centered buttons
            if st.button("Send"):
                if user_input:
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": user_input
                    })
                    enhanced_prompt = get_enhanced_prompt(
                        user_input,
                        context=str(st.session_state.chat_history)
                    )
                    response = get_gemini_response(enhanced_prompt)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })
                    st.experimental_rerun()

            if st.button("Clear Chat History"):
                st.session_state.chat_history = []
                st.session_state.support_stage = "welcome"
                st.experimental_rerun()


if __name__ == "__main__":
    main()
