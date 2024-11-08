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
    return Image.open("logo.jpg")

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
    st.sidebar.image(load_logo(), use_column_width=True)
    st.title("LaserTech Support Assistant")

    # Welcome stage
    if st.session_state.support_stage == "welcome":
        st.markdown(WELCOME_MESSAGE)
        st.session_state.chat_history = []  # Clear history on new session

        if st.button("Start Support Session"):
            st.session_state.support_stage = "support"
            st.experimental_rerun()

    # Support stage
    elif st.session_state.support_stage == "support":
        # User input
        user_input = st.text_area("Describe your issue or ask a question:")

        if st.button("Send"):
            if user_input:
                # Add user message to chat history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input
                })

                # Generate enhanced prompt and get response
                enhanced_prompt = get_enhanced_prompt(
                    user_input,
                    context=str(st.session_state.chat_history)
                )
                response = get_gemini_response(enhanced_prompt)

                # Add assistant response to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })

        # Display chat history
        st.write("### Support Conversation")
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.write(f"👤 **You:** {message['content']}")
            else:
                st.write(f"🤖 **Assistant:** {message['content']}")

        # Clear chat history
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.session_state.support_stage = "welcome"
            st.experimental_rerun()

if __name__ == "__main__":
    main()
