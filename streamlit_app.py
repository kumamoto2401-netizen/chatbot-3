import streamlit as st
import requests

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses Google's Gemini API to generate responses. "
    "To use this app, you need to provide a Gemini API key, which you can get from your Google Cloud Console. "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their Gemini API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare messages for Gemini API (convert roles to Gemini format)
        gemini_messages = []
        for m in st.session_state.messages:
            gemini_messages.append(
                {
                    "role": "user" if m["role"] == "user" else "model",
                    "parts": [{"text": m["content"]}]
                }
            )

        # Gemini API endpoint
        api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={gemini_api_key}"

        headers = {"Content-Type": "application/json"}
        data = {
            "contents": gemini_messages,
            "generationConfig": {
                "maxOutputTokens": 1024,
                "temperature": 0.7,
                "topP": 0.8
            }
        }

        try:
            response = requests.post(api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            gemini_reply = result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            gemini_reply = f"API Error: {e}"

        with st.chat_message("assistant"):
            st.markdown(gemini_reply)
        st.session_state.messages.append({"role": "assistant", "content": gemini_reply})
