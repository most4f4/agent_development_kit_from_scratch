# Understanding Agent Interaction Flow in Google ADK

This document explains what happens when you ask a question to your agent, tracing through the code step-by-step.

---

## 🎯 High-Level Overview

When you type a question:

1. **Input Collection**: Your question is captured in `main.py`
2. **State Update**: The question is added to session history
3. **Agent Processing**: The agent processes your question through the Runner
4. **Response Streaming**: Events stream back from the agent
5. **Display**: The response is formatted and shown to you
6. **State Update**: The agent's response is saved to session history

---

## 📁 File Structure

### main.py

- **Purpose**: Entry point and conversation orchestration
- **Key Components**: Session setup, conversation loop, agent runner

### utils.py

- **Purpose**: Helper functions for state management and display
- **Key Components**: History tracking, state display, event processing

---

## 🔍 Detailed Walkthrough

### PART 1: Application Startup (`main.py`)

```python
async def main_async():
    APP_NAME = "Customer Support"
    USER_ID = "user_123"
```

**What happens:**

- Sets up identifiers for your application and user
- These are used to organize sessions in the session service

---

### PART 2: Session Initialization

```python
session_service = InMemorySessionService()

initial_state = {
    "user_name": "Mostafa Shahrabadi",
    "purchased_courses": [],
    "interaction_history": [],
}

new_session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    state=initial_state,
)
SESSION_ID = new_session.id
```

**What happens:**

1. Creates an in-memory session storage (data stored in RAM)
2. Defines initial state with:
   - `user_name`: User's name
   - `purchased_courses`: List of courses (starts empty)
   - `interaction_history`: Conversation history (starts empty)
3. Creates a new session with this initial state
4. Gets back a unique `SESSION_ID` to track this conversation

**Why this matters:**

- The state persists across multiple questions in the same session
- Agents can read/write to this state to remember things
- Each conversation gets its own session ID

---

### PART 3: Runner Setup

```python
runner = Runner(
    agent=customer_service_agent,
    app_name=APP_NAME,
    session_service=session_service,
)
```

**What happens:**

- Creates a `Runner` object that manages agent execution
- Links the agent to the session service
- The runner handles the connection between your queries and the agent

**Runner's job:**

- Takes user input
- Passes it to the agent
- Manages session state
- Streams back responses

---

### PART 4: Conversation Loop (Where Questions are Asked)

```python
while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    # Step 1: Add user query to history
    add_user_query_to_history(
        session_service, APP_NAME, USER_ID, SESSION_ID, user_input
    )

    # Step 2: Process the query
    await call_agent_async(runner, USER_ID, SESSION_ID, user_input)
```

**What happens:**

1. **Input Collection**: Waits for you to type a question
2. **Exit Check**: Checks if you want to quit
3. **History Update**: Saves your question to session state
4. **Agent Call**: Sends your question to the agent for processing

**Let's say you type: "What courses do you offer?"**

---

### PART 5: Adding Query to History (`utils.py`)

```python
def add_user_query_to_history(session_service, app_name, user_id, session_id, query):
    update_interaction_history(
        session_service,
        app_name,
        user_id,
        session_id,
        {
            "action": "user_query",
            "query": query,
        },
    )
```

**What happens:**

1. Calls `update_interaction_history` with your question
2. Creates an entry like:
   ```python
   {
       "action": "user_query",
       "query": "What courses do you offer?",
       "timestamp": "2025-11-02 14:30:00"
   }
   ```

---

```python
def update_interaction_history(session_service, app_name, user_id, session_id, entry):
    # Get current session
    session = session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    # Get current interaction history
    interaction_history = session.state.get("interaction_history", [])

    # Add timestamp
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append the entry
    interaction_history.append(entry)

    # Update state
    updated_state = session.state.copy()
    updated_state["interaction_history"] = interaction_history

    # Save back to session
    session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state=updated_state,
    )
```

**What happens:**

1. **Retrieves** the current session from memory
2. **Gets** the existing interaction history (a list)
3. **Adds** a timestamp to your query entry
4. **Appends** your query to the history list
5. **Creates** a new version of the state with updated history
6. **Saves** it back to the session service

**After this step, session state looks like:**

```python
{
    "user_name": "Brandon Hancock",
    "purchased_courses": [],
    "interaction_history": [
        {
            "action": "user_query",
            "query": "What courses do you offer?",
            "timestamp": "2025-11-02 14:30:00"
        }
    ]
}
```

---

### PART 6: Calling the Agent (`utils.py`)

```python
async def call_agent_async(runner, user_id, session_id, query):
    # Create a Content object (required by ADK)
    content = types.Content(role="user", parts=[types.Part(text=query)])

    print(f"--- Running Query: {query} ---")

    final_response_text = None
    agent_name = None

    # Display state BEFORE agent processes it
    display_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State BEFORE processing",
    )
```

**What happens:**

1. **Creates** a `Content` object with your question

   - This is the format the ADK expects (similar to chat messages)
   - `role="user"` means this is from the user
   - `parts=[types.Part(text=query)]` wraps your text

2. **Displays** the current session state before the agent runs
   - Shows user name, courses, interaction history
   - Helps you see what the agent "knows" before it responds

---

### PART 7: Running the Agent (The Core Magic!)

```python
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            # Capture the agent name
            if event.author:
                agent_name = event.author

            # Process each event
            response = await process_agent_response(event)
            if response:
                final_response_text = response
    except Exception as e:
        print(f"ERROR during agent run: {e}")
```

**What happens:**

1. **Calls** `runner.run_async()` with:

   - Your user ID (who's asking)
   - Your session ID (which conversation)
   - Your message (the question)

2. **Streams events** back as they happen (this is asynchronous!)

   - Events come in real-time as the agent processes
   - Each event represents a step in the agent's thinking

3. **For each event:**
   - Extracts the agent's name (which agent is responding)
   - Processes the event with `process_agent_response()`
   - Saves the final response when it arrives

---

### PART 8: Processing Agent Events (`utils.py`)

```python
async def process_agent_response(event):
    print(f"Event ID: {event.id}, Author: {event.author}")

    # Check for text in parts
    has_specific_part = False
    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "text") and part.text and not part.text.isspace():
                print(f"  Text: '{part.text.strip()}'")

    # Check for final response
    final_response = None
    if not has_specific_part and event.is_final_response():
        if event.content and event.content.parts:
            final_response = event.content.parts[0].text.strip()
            # Display with fancy formatting
            print(f"╔═══ AGENT RESPONSE ═══════════════════════")
            print(f"{final_response}")
            print(f"╚═══════════════════════════════════════════")

    return final_response
```

**What happens:**

**Understanding Events:**

- Each `event` is a message from the agent
- Events can contain:
  - Tool calls (agent using a function)
  - Thinking steps (agent reasoning)
  - Final response (the answer for you)

**Event Processing:**

1. **Prints** event metadata (ID, author)
2. **Checks** for text content in the event
3. **Detects** if this is the final response
4. **Formats** and displays the final answer with colors and boxes

**Example event flow for "What courses do you offer?":**

```
Event 1: Agent thinking...
  ID: evt_001, Author: customer_service_agent
  Text: 'I need to check the available courses'

Event 2: Tool call...
  ID: evt_002, Author: customer_service_agent
  Text: 'Calling list_courses tool'

Event 3: Tool response...
  ID: evt_003, Author: system
  Text: 'Courses: AI Fundamentals, Python Mastery...'

Event 4: Final response...
  ID: evt_004, Author: customer_service_agent
  ╔═══ AGENT RESPONSE ═══════════════════════
  We offer the following courses:
  1. AI Fundamentals
  2. Python Mastery
  3. Data Science Bootcamp
  ╚═══════════════════════════════════════════
```

---

### PART 9: Saving Agent Response to History

```python
    # After all events are processed
    if final_response_text and agent_name:
        add_agent_response_to_history(
            runner.session_service,
            runner.app_name,
            user_id,
            session_id,
            agent_name,
            final_response_text,
        )
```

**What happens:**

1. **Checks** if we got a final response
2. **Calls** `add_agent_response_to_history()` to save it
3. **Updates** session state with the agent's answer

---

```python
def add_agent_response_to_history(
    session_service, app_name, user_id, session_id, agent_name, response
):
    update_interaction_history(
        session_service,
        app_name,
        user_id,
        session_id,
        {
            "action": "agent_response",
            "agent": agent_name,
            "response": response,
        },
    )
```

**What happens:**

- Creates an entry with the agent's response
- Adds it to interaction history (same process as user query)

**Session state now looks like:**

```python
{
    "user_name": "Brandon Hancock",
    "purchased_courses": [],
    "interaction_history": [
        {
            "action": "user_query",
            "query": "What courses do you offer?",
            "timestamp": "2025-11-02 14:30:00"
        },
        {
            "action": "agent_response",
            "agent": "customer_service_agent",
            "response": "We offer the following courses: 1. AI Fundamentals...",
            "timestamp": "2025-11-02 14:30:05"
        }
    ]
}
```

---

### PART 10: Displaying Updated State

```python
    # Display state AFTER processing
    display_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State AFTER processing",
    )
```

**What happens:**

- Shows the updated session state
- You can see how the state changed during the interaction

---

```python
def display_state(session_service, app_name, user_id, session_id, label="Current State"):
    session = session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    print(f"\n{'-' * 10} {label} {'-' * 10}")

    # Display user name
    user_name = session.state.get("user_name", "Unknown")
    print(f"👤 User: {user_name}")

    # Display purchased courses
    purchased_courses = session.state.get("purchased_courses", [])
    if purchased_courses:
        print("📚 Courses:")
        for course in purchased_courses:
            print(f"  - {course}")
    else:
        print("📚 Courses: None")

    # Display interaction history
    interaction_history = session.state.get("interaction_history", [])
    if interaction_history:
        print("📝 Interaction History:")
        for idx, interaction in enumerate(interaction_history, 1):
            if interaction.get("action") == "user_query":
                print(f'  {idx}. User query: "{interaction["query"]}"')
            elif interaction.get("action") == "agent_response":
                response = interaction["response"]
                if len(response) > 100:
                    response = response[:97] + "..."
                print(f'  {idx}. Agent response: "{response}"')
```

**What happens:**

1. **Retrieves** the current session
2. **Formats** and displays:
   - 👤 User name
   - 📚 Purchased courses (if any)
   - 📝 Interaction history (all questions and answers)
3. **Truncates** long responses (shows first 100 characters)

**Example output:**

```
---------- State AFTER processing ----------
👤 User: Brandon Hancock
📚 Courses: None
📝 Interaction History:
  1. User query: "What courses do you offer?"
  2. Agent response: "We offer the following courses: 1. AI Fundamentals, 2. Python Mastery, 3. Data..."
--------------------------------------------
```

---

## 🔄 Complete Flow Diagram

```
1. You type question
   ↓
2. Question added to session history
   ↓
3. Session state displayed (BEFORE)
   ↓
4. Question sent to Runner
   ↓
5. Runner passes to Agent
   ↓
6. Agent processes (may use tools, think, etc.)
   ↓
7. Events stream back (tool calls, thinking, response)
   ↓
8. Each event processed and displayed
   ↓
9. Final response formatted and shown
   ↓
10. Response added to session history
    ↓
11. Session state displayed (AFTER)
    ↓
12. Loop back to step 1 (waiting for next question)
```

---

## 🎓 Key Concepts Explained

### Session State

- **What**: A dictionary storing data about the conversation
- **Where**: Stored in `session_service` (in memory or database)
- **Why**: Allows the agent to "remember" things between questions
- **Contents**: user_name, purchased_courses, interaction_history

### Runner

- **What**: Object that manages agent execution
- **Job**:
  - Takes user input
  - Passes to agent
  - Manages session state
  - Returns responses
- **Why**: Abstracts away complexity of agent communication

### Events

- **What**: Messages streaming from the agent as it works
- **Types**:
  - Thinking/reasoning events
  - Tool call events
  - Tool response events
  - Final response events
- **Why**: Allows real-time display of agent activity

### Interaction History

- **What**: List of all questions and answers in the conversation
- **Structure**:
  ```python
  [
      {"action": "user_query", "query": "...", "timestamp": "..."},
      {"action": "agent_response", "agent": "...", "response": "...", "timestamp": "..."}
  ]
  ```
- **Why**: Agent can reference past conversation, you can audit interactions

---

## 💡 Important Details

### Why Two State Displays?

```python
display_state(..., "State BEFORE processing")
# ... agent processes ...
display_state(..., "State AFTER processing")
```

**Reason**: Shows you exactly what changed during agent execution

- **BEFORE**: What the agent knew when it started
- **AFTER**: What the agent knows now (including any state changes it made)

### Why Async/Await?

```python
async def call_agent_async(...)
    async for event in runner.run_async(...)
```

**Reason**: Agents can take time to respond

- `async` allows other code to run while waiting
- Events can stream in real-time
- More responsive application

### Why Create New Session Each Update?

```python
session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id,  # Same ID
    state=updated_state,     # Updated state
)
```

**Reason**: This is how `InMemorySessionService` updates state

- Passing same `session_id` overwrites the existing session
- Alternative: Use `update_session_state()` method
- For `DatabaseSessionService`, this would update the database record

---

## 🛠️ What Agents Can Do With State

Agents have access to the session state through `ToolContext`:

```python
def some_tool(param: str, tool_context: ToolContext) -> dict:
    # Read from state
    user_name = tool_context.state.get("user_name")

    # Write to state
    tool_context.state["last_action"] = "purchased_course"
    tool_context.state["purchased_courses"].append("New Course")

    return {"status": "success"}
```

**This allows agents to:**

- Remember user preferences
- Track conversation context
- Store intermediate results
- Maintain application state

---

## 🚀 Summary

**When you ask a question:**

1. ✍️ Your question is captured and timestamped
2. 💾 Question is saved to session history
3. 📊 Current state is displayed
4. 🤖 Question is sent to the agent via Runner
5. ⚡ Agent processes (may use tools, reason, etc.)
6. 📡 Events stream back in real-time
7. 🎨 Events are formatted and displayed
8. 📝 Final response is saved to session history
9. 📊 Updated state is displayed
10. 🔄 Ready for your next question

**The session state persists across all questions in the same conversation, allowing the agent to maintain context and "remember" information!**
