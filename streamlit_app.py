import streamlit as st
import requests

# Show title and description.
st.title("💬 Chatbot (Gemini Flash)")
st.write(
    "This is a simple chatbot that uses Google's Gemini API (gemini-flash-2.5) to generate responses. "
    "To use this app, you need to provide a Gemini API key via Streamlit Secrets. "
    "Learn more about [Streamlit Secrets](https://docs.streamlit.io/develop/concepts/connections/secrets-management)."
)

# Streamlit Community CloudのSecretsからAPIキーを取得
# .streamlit/secrets.toml に GEMINI_API_KEY = "YOUR_API_KEY" を設定してください
gemini_api_key = st.secrets.get("GEMINI_API_KEY")

if not gemini_api_key:
    st.info("Streamlit Community CloudのSecretsに `GEMINI_API_KEY` を設定してください。", icon="🗝️")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message.
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

        # Gemini API endpoint (モデル名を gemini-flash-2.5 に変更)
        api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-flash-2.5:generateContent?key={gemini_api_key}"

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
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                with st.spinner("Generating response..."):
                    response = requests.post(api_url, headers=headers, json=data, timeout=30)
                    response.raise_for_status() # エラーがあれば例外を発生
                    
                    result = response.json()
                    
                    # APIからのレスポンス構造のチェック
                    if "candidates" in result and result["candidates"] and \
                       "content" in result["candidates"][0] and \
                       "parts" in result["candidates"][0]["content"] and \
                       result["candidates"][0]["content"]["parts"]:
                        
                        gemini_reply = result["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        # 予期しないレスポンス形式の場合
                        gemini_reply = f"Error: Unexpected API response format. {result}"

                    st.markdown(gemini_reply)
            
            # Store the assistant's response.
            st.session_state.messages.append({"role": "assistant", "content": gemini_reply})

        except requests.exceptions.RequestException as e:
            st.error(f"API Request Error: {e}")
            gemini_reply = f"API Request Error: {e}"
            # エラー時もセッションに保存（オプション）
            # st.session_state.messages.append({"role": "assistant", "content": gemini_reply})
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            gemini_reply = f"An unexpected error occurred: {e}"
            # エラー時もセッションに保存（オプション）
            # st.session_state.messages.append({"role": "assistant", "content": gemini_reply})
