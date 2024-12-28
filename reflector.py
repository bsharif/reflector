import streamlit as st
import openai

# 1. Set up OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("OpenAI Assistants Quickstart")

st.markdown("""
This app demonstrates how to use OpenAI's Assistants Beta API to manage conversation threads.
""")

# 2. Check for existing thread in session state
if "thread_id" not in st.session_state:
    try:
        # 3. Create a new thread
        thread = openai.beta.threads.create(
            thread={
                "assistant_id": "asst_CFGa7zG3plj8gNr0uXFzuaK4",  # Include assistant_id here
                "messages": []  # Start with an empty thread or include system messages
            }
        )
        # Save thread ID to session state
        st.session_state["thread_id"] = thread["id"]
        st.success(f"Created new thread with ID: {thread['id']}")

    except Exception as e:
        st.error(f"Failed to create a new thread: {e}")

# 4. Input for user prompt
user_prompt = st.text_input("Enter your message to the assistant:")

# 5. Button to send the user’s message
if st.button("Send"):
    if user_prompt.strip():
        try:
            thread_id = st.session_state["thread_id"]

            # 6. Run a message on the existing thread
            run = openai.beta.threads.runs.create(
                thread_id=thread_id,
                run={
                    "messages": [
                        {"role": "user", "content": user_prompt}
                    ]
                }
            )

            # 7. Extract the assistant's reply from the updated thread
            assistant_reply = ""
            if "thread" in run and "messages" in run["thread"]:
                messages = run["thread"]["messages"]
                for msg in messages:
                    if msg["role"] == "assistant":
                        assistant_reply = msg["content"]

            if assistant_reply:
                st.markdown(f"**Assistant:** {assistant_reply}")
            else:
                st.warning("No assistant reply found.")

        except Exception as e:
            st.error(f"Failed to send message to the thread: {e}")
    else:
        st.warning("Please enter a message before sending.")

# 8. Button to show full conversation
if st.button("Show conversation"):
    try:
        thread_id = st.session_state["thread_id"]
        thread = openai.beta.threads.get(thread_id=thread_id)
        st.write("### Full Conversation")
        for msg in thread["messages"]:
            role = msg["role"].capitalize()
            content = msg["content"]
            st.markdown(f"**{role}:** {content}")
    except Exception as e:
        st.error(f"Failed to retrieve conversation: {e}")