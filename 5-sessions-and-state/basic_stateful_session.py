import uuid
import os
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from question_answering_agent import question_answering_agent

# Load environment variables from .env file in the current directory
load_dotenv()

# Create a new session service to store state
session_service_stateful = InMemorySessionService()

# Define initial state for the session
initial_state = {
    "user_name": "Mostafa Shahrabadi",
    "user_preferences": """
        I like to play Snooker, Table Tennis, and Back Gammon.
        My favorite food is Persian.
        My favorite TV show is Better Call Saul.
    """,
}

# Define metadata for the session
APP_NAME = "Mostafa's Bot"
USER_ID = "mostafa_shahrabadi"
SESSION_ID = str(uuid.uuid4())

# Create a new stateful session with the initial state
stateful_session = session_service_stateful.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
    state=initial_state,
)
print("CREATED NEW SESSION:")
print(f"\tSession ID: {SESSION_ID}")

# Create a Runner with the stateful session service
runner = Runner(
    agent=question_answering_agent,
    app_name=APP_NAME,
    session_service=session_service_stateful,
)

# Send a message to the agent within the session
# Note: The types.Content and types.Part are used to structure the message
new_message = types.Content(
    role="user", parts=[types.Part(text="What is Mostafa's favorite TV show?")]
)

# Run the runner with the new message and print the final response
for event in runner.run(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=new_message,
):
    # Print only the final response from the agent (because there may be intermediate tool calls)
    if event.is_final_response():
        # Check if content exists before accessing parts to avoid errors
        if event.content and event.content.parts:
            print(f"Final Response: {event.content.parts[0].text}")

print("==== Session Event Exploration ====")
session = session_service_stateful.get_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)

# Log final Session state
print("=== Final Session State ===")
for key, value in session.state.items():
    print(f"{key}: {value}")
