from openai import OpenAI
from pprint import pprint
import time


api_key = "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"

client = OpenAI(api_key=api_key)



assistant = client.beta.assistants.retrieve("asst_CFGa7zG3plj8gNr0uXFzuaK4")
# pprint(assistant)



thread = client.beta.threads.create()
# pprint(thread)
message = client.beta.threads.messages.create(
thread_id=thread.id,
role="user",
content="Write a reflection on an emergency anaesthetic",
)

run = client.beta.threads.runs.create(
thread_id=thread.id,
assistant_id=assistant.id,
)

# pprint(run)

time.sleep(20)

if run.status == 'completed': 
    messages = client.beta.threads.messages.list(
    thread_id=thread.id
)
    pprint(messages)
# else:
#     print(run.status)

pprint(run.status)