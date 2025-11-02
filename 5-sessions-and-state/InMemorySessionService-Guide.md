# Beginner's Guide to InMemorySessionService in Google ADK

## What is InMemorySessionService?

InMemorySessionService is a session management system that stores all session data in your application's memory (RAM). This means sessions exist only while your application is running and will be lost when the application stops or restarts.

**Best for:** Development, testing, demos, and temporary short-lived interactions.

---

## Getting Started

### Basic Setup

```python
from google.adk.sessions import InMemorySessionService

# Initialize the service
session_service = InMemorySessionService()
```

That's it! No configuration needed. Sessions are now stored in memory.

---

## Core Functions You Need to Know

### 1. Creating a New Session

Start a new session for a user:

```python
# Create a session with initial state
new_session = await session_service.create_session(
    app_name="my_chat_app",
    user_id="user123",
    state={"conversation_topic": "weather", "message_count": 0}
)

print(f"Session created with ID: {new_session.id}")
```

**What you get back:** A session object with a unique `id`, the `app_name`, `user_id`, `created_at` timestamp, and your initial `state`.

---

### 2. Listing All Sessions

See all sessions for a specific user and app:

```python
# Get all sessions for a user
sessions = session_service.list_sessions(
    app_name="my_chat_app",
    user_id="user123"
)

print(f"Found {len(sessions)} sessions")
for session in sessions:
    print(f"- Session {session.id}: created at {session.created_at}")
```

**Use case:** Check if a user has existing sessions before creating a new one.

---

### 3. Getting a Specific Session

Retrieve one session by its ID:

```python
# Load an existing session
session = session_service.get_session(
    app_name="my_chat_app",
    user_id="user123",
    session_id="abc-123-def"
)

print(f"Current state: {session.state}")
```

**Use case:** Resume a conversation or retrieve stored context.

---

### 4. Updating Session State

Modify the data stored in a session:

```python
# Update the session's state dictionary
await session_service.update_session_state(
    session_id="abc-123-def",
    state={"conversation_topic": "sports", "message_count": 5}
)
```

**Important:** This replaces the entire state dictionary. To preserve existing data, merge it yourself:

```python
# Get current state
session = session_service.get_session(app_name, user_id, session_id)
current_state = session.state

# Merge with new data
updated_state = {**current_state, "new_key": "new_value"}

# Update
await session_service.update_session_state(session_id, updated_state)
```

---

### 5. Deleting a Session

Remove a session when you're done with it:

```python
# Delete a single session
session_service.delete_session(session_id="abc-123-def")
```

**Use case:** Clean up completed conversations or expired sessions.

---

### 6. Clearing All Sessions

Remove all sessions for a user/app combination:

```python
# Delete all sessions for a user
session_service.clear_sessions(
    app_name="my_chat_app",
    user_id="user123"
)
```

**Use case:** Reset during development or when a user logs out.

---

## Understanding the Session Object

Every session has these key attributes:

```python
session.id          # Unique identifier (string)
session.app_name    # Your application name
session.user_id     # The user this session belongs to
session.created_at  # When it was created (datetime)
session.state       # Dictionary with your custom data
```

---

## Common Beginner Pattern

Here's a typical flow for managing sessions:

```python
from google.adk.sessions import InMemorySessionService

# Setup
session_service = InMemorySessionService()
APP_NAME = "my_chat_app"
USER_ID = "user123"

async def get_or_create_session():
    # Check for existing sessions
    existing_sessions = session_service.list_sessions(
        app_name=APP_NAME,
        user_id=USER_ID
    )
    
    if existing_sessions:
        # Use the most recent session
        session = existing_sessions[0]
        print(f"Resuming session {session.id}")
    else:
        # Create a new session
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            state={"message_count": 0}
        )
        print(f"Created new session {session.id}")
    
    return session

# Use it
session = await get_or_create_session()

# Update state during conversation
current_count = session.state.get("message_count", 0)
await session_service.update_session_state(
    session.id,
    {"message_count": current_count + 1}
)

# Clean up when done
session_service.delete_session(session.id)
```

---

## Pros and Cons

### ✅ Advantages
- **Fast:** No database overhead
- **Simple:** No setup or configuration required
- **Great for testing:** Quick iteration during development

### ❌ Limitations
- **Not persistent:** Data lost when app restarts
- **Not scalable:** Can't share sessions across multiple servers
- **Memory limits:** Large numbers of sessions consume RAM

---

## When to Use InMemorySessionService

**Good for:**
- Local development and testing
- Proof-of-concepts and demos
- Short-lived, temporary sessions
- Single-server applications with low traffic

**Not good for:**
- Production applications
- Long-term session storage
- Multi-server deployments
- Applications that need to survive restarts

---

## Quick Reference

| Function | Purpose |
|----------|---------|
| `create_session()` | Start a new session |
| `list_sessions()` | Get all sessions for a user |
| `get_session()` | Retrieve a specific session |
| `update_session_state()` | Modify session data |
| `delete_session()` | Remove a session |
| `clear_sessions()` | Remove all sessions for a user |

---

## Next Steps

Once you're comfortable with InMemorySessionService, consider:
1. Learning DatabaseSessionService for persistent storage
2. Implementing session expiration logic
3. Adding session metadata (tags, timestamps)
4. Building session recovery mechanisms

Happy coding! 🚀
