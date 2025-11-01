# Sessions and State Management in ADK

This example demonstrates how to create and manage stateful sessions in the Agent Development Kit (ADK), enabling your agents to maintain context and remember user information across interactions.

## What Are Sessions in ADK?

A state in ADK is combination of:

- **Session State**: Custom key-value pairs defined by the developer to store user-specific information
- **Event History**: Automatically managed by ADK to keep track of user messages, tool calls, and agent responses
- **Additional Information**: identifiers like `session_id`, `app_name`, `user_id`, `last_update_time`, etc.

Sessions allow agents to maintain context over multiple interactions with users. Unlike simple conversational agents that forget previous interactions, stateful agents can build relationships with users over time by remembering important details and preferences.

### Session Types in ADK

ADK supports different session storage mechanisms:

- **InMemorySessionService**: Stored in memory, suitable for development and testing
- **DatabaseSessionService**: Persistent storage using databases like Firestore or SQL databases
- **VertexAISessionService**: Managed sessions using Vertex AI for scalable applications

### Session Properties

```python
 from google.adk.sessions import InMemorySessionService, Session

 # Create a simple session to examine its properties
 temp_service = InMemorySessionService()
 example_session = await temp_service.create_session(
     app_name="my_app",
     user_id="example_user",
     state={"initial_key": "initial_value"} # State can be initialized
 )

 print(f"--- Examining Session Properties ---")
 print(f"ID (`id`):                {example_session.id}")
 print(f"Application Name (`app_name`): {example_session.app_name}")
 print(f"User ID (`user_id`):         {example_session.user_id}")
 print(f"State (`state`):           {example_session.state}") # Note: Only shows initial state here
 print(f"Events (`events`):         {example_session.events}") # Initially empty
 print(f"Last Update (`last_update_time`): {example_session.last_update_time:.2f}")
 print(f"---------------------------------")
```

## Example Overview

This directory contains a basic stateful session example that demonstrates:

- Creating a session with user preferences
- Using template variables to access session state in agent instructions
- Running the agent with a session to maintain context

The example uses a simple question-answering agent that responds based on stored user information in the session state.

## Project Structure

```
5-sessions-and-state/
│
├── basic_stateful_session.py      # Main example script
├── .env                           # Environment variables for API keys
│
└── question_answering_agent/      # Agent implementation
    ├── __init__.py
    └── agent.py                   # Agent definition with template variables
```

## Getting Started

### Setup

1. Activate the virtual environment from the root directory:

```bash
# macOS/Linux:
source ../.venv/bin/activate
# Windows CMD:
..\.venv\Scripts\activate.bat
# Windows PowerShell:
..\.venv\Scripts\Activate.ps1
```

2. Create a `.env` file and add your Google API key:

```
GOOGLE_API_KEY=your_api_key_here
```

### Running the Example

Run the example to see a stateful session in action:

```bash
python basic_stateful_session.py
```

This will:

1. Create a new session with user information
2. Initialize the agent with access to that session
3. Process a user query about the stored preferences
4. Display the agent's response based on the session data

## Key Components

### Session Service

The example uses the `InMemorySessionService` which stores sessions in memory:

```python
session_service = InMemorySessionService()
```

### Initial State

Sessions are created with an initial state containing user information:

```python
initial_state = {
    "user_name": "Mostafa Shahrabadi",
    "user_preferences": """
        I like to play Snooker, Table Tennis, and Back Gammon.
        My favorite food is Persian.
        My favorite TV show is Better Call Saul.
    """,
}
```

### Creating a Session

The example creates a session with a unique identifier:

```python
stateful_session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
    state=initial_state,
)
```

### Accessing State in Agent Instructions

The agent accesses session state using template variables in its instructions:

```python
instruction="""
You are a helpful assistant that answers questions about the user's preferences.

Here is some information about the user:
Name:
{user_name}
Preferences:
{user_preferences}
"""
```

### What is Runner?

The `Runner` is a high-level interface in ADK that manages the interaction between the user, agent, and session service. It handles message processing, tool invocation, and session state management seamlessly.

The `Runner` is a collection of two main components: an `Agent` and a `Session`. Everything connects inside the `Runner`. The `Runner` is responsible for managing the interaction between the user and the agent, handling inputs, outputs, and any necessary processing.

### Running with Sessions

Sessions are integrated with the `Runner` to maintain state between interactions:

```python
runner = Runner(
    agent=question_answering_agent,
    app_name=APP_NAME,
    session_service=session_service,
)
```

### How It All Works Together

1. A session is created with initial user preferences.
2. Agent instructions use placeholders that reference state keys.
3. Runner automatically injects state values into the agent's instructions.
4. The agent responds based on the user's stored preferences.
5. Session persists so future messages in the same session remember the user preferences.

## Additional Resources

- [Google ADK Sessions Documentation](https://google.github.io/adk-docs/sessions/session/)
- [State Management in ADK](https://google.github.io/adk-docs/sessions/state/)
