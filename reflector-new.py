import streamlit as st
import openai
import time

# Set your OpenAI API key (from Streamlit secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("LLP Reflector")

st.markdown("""
This app helps generate reflections for anaesthetic cases and links them relevant to Stage 3 RCoA Key Capabiltities.
""")

# 1. Attempt to retrieve assistant once, e.g. on app load or in session state
if "assistant" not in st.session_state:
    try:
        # Retrieve returns an assistant object with .id, .name, etc.
        assistant = openai.beta.assistants.retrieve("asst_CFGa7zG3plj8gNr0uXFzuaK4")
        st.session_state["assistant"] = assistant
        st.success("Assistant retrieved successfully.")
    except Exception as e:
        st.error(f"Error retrieving assistant: {e}")

# 2. Initialise a new thread in session state if there isn't one already
if "thread_id" not in st.session_state:
    try:
        # Create returns a thread object with .id, etc.
        thread = openai.beta.threads.create()
        st.session_state["thread_id"] = thread.id
        st.success(f"Created new thread with ID: {thread.id}")
    except Exception as e:
        st.error(f"Failed to create a new thread: {e}")

# 3. A text input for the reflection prompt (or any other user prompt)
user_prompt = st.text_area(
    "Enter your message or reflection prompt:",
    value="Write a reflection on an anaesthetic for an emergency craniotomy for a patient with severe aortic stenosis. "
          "Consider CV stability, high NELA score, post-op ICU care, and use of epidural for analgesia."
)

# 4. Button to send the user’s message
if st.button("Send Reflection Prompt"):
    if user_prompt.strip():
        try:
            # Add a user message to the existing thread
            message = openai.beta.threads.messages.create(
                thread_id=st.session_state["thread_id"],
                role="user",
                content=user_prompt
            )

            # Create a run associated with this thread and the retrieved assistant
            run = openai.beta.threads.runs.create(
                thread_id=st.session_state["thread_id"],
                assistant_id=st.session_state["assistant"].id
            )

            # Poll until the run is completed
            with st.spinner("Waiting for the assistant to process your request..."):
                while run.status in ["queued", "in_progress"]:
                    time.sleep(5)
                    run = openai.beta.threads.runs.retrieve(
                        thread_id=st.session_state["thread_id"],
                        run_id=run.id,
                    )


            if run.status == "completed":
                st.success("Reflection generated successfully!")
            else:
                st.warning("The run did not succeed. Check the logs or run status.")

        except Exception as e:
            st.error(f"Failed to create or complete the run: {e}")
    else:
        st.warning("Please enter a message before sending.")

    # 5. Button to show full conversation (retrieve all messages from the thread)
    try:
        # messages is typically an object with a .data attribute containing the list
        all_messages = openai.beta.threads.messages.list(thread_id=st.session_state["thread_id"])
        st.write("### Full Conversation")

        # The messages list is in all_messages.data
        for msg in reversed(all_messages.data):
            role = msg.role.capitalize()
            text_content = ""

            # Each message can have .content which might be a list of text/function blocks
            if msg.content and isinstance(msg.content, list):
                for part in msg.content:
                    if hasattr(part, "text") and hasattr(part.text, "value"):
                        text_content += part.text.value

            st.markdown(f"**{role}:** {text_content}")

    except Exception as e:
        st.error(f"Failed to retrieve conversation: {e}")