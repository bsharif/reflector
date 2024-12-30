import streamlit as st
import openai
import time

# Set your OpenAI API key (retrieved securely from Streamlit secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("LLP Reflector")

st.markdown("""
This app helps generate reflections for anaesthetic cases and links them to relevant RCoA Key Capabilities.
""")

# Dictionary mapping training stages to assistant IDs
assistants = {
    "Stage 1": "asst_BlfkrEk2hCqj3GJ8xGbA6Ec9",
    "Stage 2": "asst_HMy6bcRxj7306vVp9X1WNQCl",
    "Stage 3": "asst_VYi6rqjobkudVZpnnowv4tJF",
}

# Initialise a new thread in session state if it doesn't already exist
if "thread_id" not in st.session_state:
    try:
        thread = openai.beta.threads.create()
        st.session_state["thread_id"] = thread.id
        # st.success(f"Created new thread with ID: {thread.id}")
    except Exception as e:
        st.error(f"Failed to create a new thread: {e}")

# Dropdown menu for the user to select their training stage
selected_stage = st.selectbox(
    "Select your training stage",
    ("Stage 1", "Stage 2", "Stage 3"),
)

# Text input area for the user to provide their reflection prompt
user_prompt = st.text_area(
    "Enter your message or reflection prompt:",
    value=st.session_state.get("last_prompt", ""),
    key="prompt_input"
)

# Button to submit the reflection prompt
if st.button("Send Reflection Prompt"):
    if "assistant" not in st.session_state:
        try:
            assistant = openai.beta.assistants.retrieve(assistants[selected_stage])
            st.session_state["assistant"] = assistant
            st.success(f"Assistant retrieved successfully for {selected_stage}")
        except Exception as e:
            st.error(f"Error retrieving assistant: {e}")
            st.stop()

    if user_prompt.strip():
        try:
            # Add the user's message to the thread
            message = openai.beta.threads.messages.create(
                thread_id=st.session_state["thread_id"],
                role="user",
                content=user_prompt
            )

            # Create a run to process the user's request
            run = openai.beta.threads.runs.create(
                thread_id=st.session_state["thread_id"],
                assistant_id=st.session_state["assistant"].id
            )

            # Wait for the assistant to process the request
            with st.spinner("Waiting for the assistant to process your request..."):
                while run.status in ["queued", "in_progress"]:
                    time.sleep(5)
                    run = openai.beta.threads.runs.retrieve(
                        thread_id=st.session_state["thread_id"],
                        run_id=run.id,
                    )

            # Display the messages if the run is completed
            if run.status == "completed":
                st.success("Reflection generated successfully!")

                # Retrieve and display all messages
                try:
                    all_messages = openai.beta.threads.messages.list(
                        thread_id=st.session_state["thread_id"]
                    )
                    # st.write("### Full Conversation")
                    for msg in reversed(all_messages.data):
                        role = msg.role.capitalize()
                        text_content = ""
                        if msg.content and isinstance(msg.content, list):
                            for part in msg.content:
                                if hasattr(part, "text") and hasattr(part.text, "value"):
                                    text_content += part.text.value
                        st.markdown(f"**{role}:** \n\n {text_content}")
                except Exception as e:
                    st.error(f"Failed to retrieve conversation: {e}")

                # Reset the thread and input for the next run
                try:
                    thread = openai.beta.threads.create()
                    st.session_state["thread_id"] = thread.id
                    del st.session_state["assistant"] 
                    st.session_state["last_prompt"] = ""  # Clear the input box
                    st.success("Ready for the next reflection!")
                except Exception as e:
                    st.error(f"Failed to reset the thread: {e}")
            else:
                st.warning("The run did not succeed. Check the logs or run status.")
        except Exception as e:
            st.error(f"Failed to create or complete the run: {e}")
    else:
        st.warning("Please enter a message before sending.")