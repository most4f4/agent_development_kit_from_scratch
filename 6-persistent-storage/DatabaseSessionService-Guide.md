# Beginner's Guide to DatabaseSessionService in Google ADK

## What is DatabaseSessionService?

DatabaseSessionService is a session management system that stores all session data in a database. Unlike in-memory storage, sessions persist even when your application restarts, making it suitable for production environments.

**Best for:** Production applications, multi-server deployments, and any scenario requiring persistent session storage.

---

## Getting Started

### Basic Setup

```python
from google.adk.sessions import DatabaseSessionService

# Initialize with SQLite (good for getting started)
db_url = "sqlite:///./my_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)
```

The database file `my_agent_data.db` will be created automatically in your current directory.

### Other Database Options

```python
# PostgreSQL (production recommended)
db_url = "postgresql://user:password@localhost:5432/my_database"

# MySQL
db_url = "mysql://user:password@localhost:3306/my_database"

# PostgreSQL with async support
db_url = "postgresql+asyncpg://user:password@localhost:5432/my_database"
```

---

## Core Functions You Need to Know

### 1. Creating a New Session

Start a new session that persists in the database:

```python
# Create a session with initial state
new_session = await session_service.create_session(
    app_name="my_chat_app",
    user_id="user456",
    state={"language": "en", "preferences": {"theme": "dark"}}
)

print(f"Session created with ID: {new_session.id}")
print(f"This session is now saved in the database!")
```

**What happens:** The session is immediately written to your database and will survive application restarts.

---

### 2. Listing All Sessions

Retrieve all sessions for a user from the database:

```python
# Get all sessions for a user
sessions = session_service.list_sessions(
    app_name="my_chat_app",
    user_id="user456"
)

print(f"Found {len(sessions)} sessions in database")
for session in sessions:
    print(f"- Session {session.id}: created at {session.created_at}")
    print(f"  State: {session.state}")
```

**Use case:** Show a user their conversation history or let them choose which conversation to continue.

---

### 3. Getting a Specific Session

Load one session from the database:

```python
# Retrieve a session by ID
session = session_service.get_session(
    app_name="my_chat_app",
    user_id="user456",
    session_id="xyz-789-abc"
)

if session:
    print(f"Loaded session state: {session.state}")
else:
    print("Session not found")
```

**Use case:** Resume a specific conversation or retrieve user preferences.

---

### 4. Updating Session State

Modify session data and persist changes:

```python
# Update the session's state
await session_service.update_session_state(
    session_id="xyz-789-abc",
    state={"language": "es", "message_count": 10}
)

print("State updated in database")
```

**Important:** Like InMemorySessionService, this replaces the entire state. To preserve existing data:

```python
# Get current session
session = session_service.get_session(app_name, user_id, session_id)

# Merge with new data
updated_state = {
    **session.state,
    "last_topic": "weather",
    "message_count": session.state.get("message_count", 0) + 1
}

# Save back to database
await session_service.update_session_state(session_id, updated_state)
```

---

### 5. Deleting a Session

Permanently remove a session from the database:

```python
# Delete a single session
session_service.delete_session(session_id="xyz-789-abc")
print("Session removed from database")
```

**Use case:** Clean up old conversations, implement data retention policies, or handle user deletion requests.

---

### 6. Clearing All Sessions

Remove all sessions for a user/app from the database:

```python
# Delete all sessions for a user
session_service.clear_sessions(
    app_name="my_chat_app",
    user_id="user456"
)
print("All sessions cleared from database")
```

**Use case:** User logout, account deletion, or resetting user data.

---

## Understanding the Session Object

Every session stored in the database has:

```python
session.id          # Unique identifier (string)
session.app_name    # Your application name
session.user_id     # The user this session belongs to
session.created_at  # When it was created (datetime)
session.updated_at  # When it was last modified (datetime)
session.state       # Dictionary with your custom data (stored as JSON)
```

**Note:** The `state` dictionary is serialized as JSON in the database, so it can store strings, numbers, lists, and nested objects.

---

## Complete Example: Building a Chat Bot

Here's a realistic example showing how to manage sessions in a production-style app:

```python
from google.adk.sessions import DatabaseSessionService
import asyncio

# Setup
db_url = "sqlite:///./chatbot_data.db"
session_service = DatabaseSessionService(db_url=db_url)

APP_NAME = "customer_support_bot"

async def handle_user_message(user_id: str, message: str):
    """Process a message and maintain session state"""
    
    # Find or create session
    existing_sessions = session_service.list_sessions(
        app_name=APP_NAME,
        user_id=user_id
    )
    
    if existing_sessions:
        # Use most recent session
        session = existing_sessions[0]
        print(f"Continuing session {session.id}")
    else:
        # Create new session
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            state={
                "message_count": 0,
                "conversation_history": [],
                "user_name": None
            }
        )
        print(f"Started new session {session.id}")
    
    # Get current state
    state = session.state
    
    # Update conversation
    state["message_count"] += 1
    state["conversation_history"].append({
        "role": "user",
        "content": message
    })
    
    # Simple bot response
    if state["message_count"] == 1:
        response = "Hello! What's your name?"
    elif state["user_name"] is None and state["message_count"] == 2:
        state["user_name"] = message
        response = f"Nice to meet you, {message}! How can I help you today?"
    else:
        response = f"Thanks for your message, {state['user_name']}!"
    
    state["conversation_history"].append({
        "role": "assistant",
        "content": response
    })
    
    # Save updated state to database
    await session_service.update_session_state(session.id, state)
    
    return response

# Test it
async def main():
    user_id = "customer_001"
    
    # Simulate conversation
    print(await handle_user_message(user_id, "Hi there!"))
    print(await handle_user_message(user_id, "My name is Alice"))
    print(await handle_user_message(user_id, "I need help with my order"))
    
    # Show all sessions (persisted in database)
    sessions = session_service.list_sessions(APP_NAME, user_id)
    print(f"\nTotal sessions in database: {len(sessions)}")
    print(f"Messages in current session: {sessions[0].state['message_count']}")

asyncio.run(main())
```

---

## Database Management Tips

### Checking Your Database

For SQLite, you can inspect your database file:

```python
import sqlite3

conn = sqlite3.connect("my_agent_data.db")
cursor = conn.cursor()

# See all sessions
cursor.execute("SELECT * FROM sessions")
rows = cursor.fetchall()
print(f"Total sessions: {len(rows)}")

conn.close()
```

### Backup and Recovery

```python
import shutil

# Backup SQLite database
shutil.copy("my_agent_data.db", "my_agent_data_backup.db")

# For production databases, use proper backup tools:
# - PostgreSQL: pg_dump
# - MySQL: mysqldump
```

### Session Cleanup

Implement periodic cleanup to remove old sessions:

```python
from datetime import datetime, timedelta

async def cleanup_old_sessions(days_old=30):
    """Delete sessions older than specified days"""
    all_sessions = session_service.list_sessions(
        app_name=APP_NAME,
        user_id=None  # Get all users
    )
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    for session in all_sessions:
        if session.created_at < cutoff_date:
            session_service.delete_session(session.id)
            print(f"Deleted old session: {session.id}")
```

---

## Pros and Cons

### ✅ Advantages
- **Persistent:** Data survives restarts and crashes
- **Scalable:** Works across multiple servers
- **Production-ready:** Reliable storage for real applications
- **Queryable:** Can analyze session data with SQL
- **Concurrent:** Multiple processes can access safely

### ❌ Considerations
- **Setup required:** Need to configure database connection
- **Slower than memory:** Database I/O has overhead
- **Requires maintenance:** Backups, cleanup, monitoring
- **Dependencies:** Need database server (except SQLite)

---

## When to Use DatabaseSessionService

**Good for:**
- Production applications
- Long-term session storage
- Multi-server deployments
- Applications with user accounts
- Compliance requirements (data retention, audit trails)
- Sharing sessions across different services

**Required for:**
- Any app that needs sessions to survive restarts
- Load-balanced applications
- Mobile or web apps with persistent users

---

## SQLite vs PostgreSQL: Which to Choose?

### SQLite (Good for Starting)
```python
db_url = "sqlite:///./my_data.db"
```
- ✅ No server setup needed
- ✅ Perfect for development
- ✅ Easy to backup (just copy the file)
- ❌ Limited concurrent writes
- ❌ Not ideal for high traffic

### PostgreSQL (Production Recommended)
```python
db_url = "postgresql://user:pass@localhost:5432/mydb"
```
- ✅ Handles high concurrency
- ✅ Better performance at scale
- ✅ Advanced features (replication, monitoring)
- ✅ Industry standard
- ❌ Requires server setup

**Pro tip:** Start with SQLite during development, then switch to PostgreSQL for production.

---

## Quick Reference

| Function | Purpose | Persists? |
|----------|---------|-----------|
| `create_session()` | Start a new session | ✅ Yes |
| `list_sessions()` | Get all sessions for a user | ✅ Reads from DB |
| `get_session()` | Retrieve a specific session | ✅ Reads from DB |
| `update_session_state()` | Modify session data | ✅ Saves to DB |
| `delete_session()` | Remove a session | ✅ Deletes from DB |
| `clear_sessions()` | Remove all sessions for a user | ✅ Deletes from DB |

---

## Common Pitfalls and Solutions

### Problem: Lost State Updates
```python
# ❌ Wrong: Direct modification doesn't save
session = session_service.get_session(app_name, user_id, session_id)
session.state["count"] = 5  # This doesn't persist!

# ✅ Correct: Use update_session_state
await session_service.update_session_state(session_id, {"count": 5})
```

### Problem: Database Connection Errors
```python
# Check your connection string carefully
# SQLite: Use three slashes for relative path
db_url = "sqlite:///./data.db"  # Correct
db_url = "sqlite://./data.db"   # Wrong!

# PostgreSQL: Include all parts
db_url = "postgresql://user:password@host:port/database"
```

### Problem: State Overwrites
```python
# ❌ This replaces entire state
await session_service.update_session_state(session_id, {"new_key": "value"})

# ✅ Merge with existing state first
session = session_service.get_session(app_name, user_id, session_id)
updated = {**session.state, "new_key": "value"}
await session_service.update_session_state(session_id, updated)
```

---

## Next Steps

1. **Try it locally:** Start with SQLite and build a simple chatbot
2. **Add features:** Implement session expiration, user preferences, conversation history
3. **Go to production:** Set up PostgreSQL and migrate your data
4. **Monitor and maintain:** Add logging, backup automation, and cleanup jobs
5. **Optimize:** Add database indexes for faster queries on large datasets

Happy building! 🚀
