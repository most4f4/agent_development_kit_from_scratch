# ADK Session Management: `adk web` vs Custom Scripts

A complete guide to understanding when and how to use ADK's built-in web interface versus custom session management.

---

## 🎯 The Core Question

**"If I manage sessions manually in my code, can I still use `adk web`?"**

**Answer: YES!** They are two different ways to run the same agent. Understanding when to use each approach will help you develop and deploy agents effectively.

---

## 📊 Quick Comparison

| Feature | `adk web` | Custom Script (`main.py`) |
|---------|-----------|---------------------------|
| **Setup Effort** | Zero (automatic) | Manual (you control everything) |
| **Session Management** | Handled by ADK | You manage it |
| **Initial State** | Empty (unless callback) | You define it |
| **Runner Setup** | Automatic | Manual |
| **Web Interface** | ✅ Included | ❌ Terminal/CLI only |
| **Database Persistence** | ❌ Memory only (default) | ✅ Your choice |
| **Custom Flows** | ❌ Limited | ✅ Full control |
| **Best For** | Development, testing | Production, complex logic |

---

## 🚀 Approach 1: Using `adk web`

### What It Does

When you run `adk web`, ADK automatically:
1. Initializes an `InMemorySessionService`
2. Creates sessions as needed
3. Sets up the `Runner`
4. Launches a web interface
5. Manages the conversation loop

### How to Use

```bash
# From parent folder (not inside agent folder)
adk web
```

### What Gets Ignored

Any custom session setup in your `main.py` is **not used**:

```python
# ❌ This code is IGNORED when using `adk web`
session_service = InMemorySessionService()
initial_state = {
    "user_name": "Mostafa",
    "purchased_courses": [],
    "interaction_history": []
}
```

### State Initialization

State starts **empty** unless you use callbacks (covered later).

### Pros & Cons

**✅ Advantages:**
- Zero configuration needed
- Instant web UI for testing
- Perfect for rapid prototyping
- Great for demos and presentations
- No need to write conversation loops

**❌ Limitations:**
- Memory-only storage (lost on restart)
- No custom initial state (without callbacks)
- Limited control over session lifecycle
- Can't implement custom business logic
- Single-user focused

### Best Use Cases

- 🧪 **Development & Testing**: Quick iteration on agent logic
- 🎨 **Prototyping**: Testing instructions and tools
- 🎯 **Demos**: Showing agent capabilities
- 📚 **Learning**: Understanding ADK basics

---

## 🛠️ Approach 2: Custom Session Management

### What You Control

When you write a custom `main.py`, you manage:
1. Session service type (memory, database, etc.)
2. Initial state values
3. Runner configuration
4. Conversation flow
5. State inspection and logging
6. Error handling

### Complete Example

```python
import asyncio
from customer_service_agent.agent import customer_service_agent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

# 1. Choose your session service
db_url = "sqlite:///./customer_data.db"
session_service = DatabaseSessionService(db_url=db_url)

# 2. Define initial state
initial_state = {
    "user_name": "Mostafa Shahrabadi",
    "purchased_courses": [],
    "interaction_history": []
}

async def main_async():
    APP_NAME = "Customer Support"
    USER_ID = "user_123"
    
    # 3. Create session with your initial state
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state
    )
    SESSION_ID = session.id
    
    # 4. Setup runner
    runner = Runner(
        agent=customer_service_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    # 5. Custom conversation loop
    print("Welcome to Customer Service!")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ["exit", "quit"]:
            break
        
        # 6. Process message
        content = types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        )
        
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content
        ):
            # Handle events
            if event.is_final_response():
                if event.content and event.content.parts:
                    response = event.content.parts[0].text
                    print(f"Agent: {response}")
        
        # 7. Optional: Inspect state
        current_session = session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        print(f"State: {current_session.state}")
    
    print("Goodbye!")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
```

### Running It

```bash
python main.py
```

### Pros & Cons

**✅ Advantages:**
- Full control over everything
- Persistent storage (database)
- Custom initial state
- Complex business logic
- Multi-user support
- Production-ready
- Custom logging and monitoring
- State inspection at any point

**❌ Limitations:**
- More code to write
- No automatic web UI
- Must handle errors yourself
- Requires understanding of async Python

### Best Use Cases

- 🏭 **Production Deployments**: Real applications
- 💾 **Persistent Storage**: Data must survive restarts
- 🔄 **Complex Workflows**: Custom conversation logic
- 👥 **Multi-User Systems**: Many users, many sessions
- 📊 **Analytics**: Track and analyze interactions
- 🔐 **Security**: Custom authentication/authorization

---

## 🔄 Approach 3: Hybrid (Best of Both Worlds)

### The Strategy

Use **callbacks** to initialize state, making your agent work seamlessly with both approaches.

### Implementation

```python
# In your agent.py
from google.adk.agents.callback_context import CallbackContext
from typing import Optional
from google.genai import types

def initialize_state_callback(
    callback_context: CallbackContext
) -> Optional[types.Content]:
    """
    Initialize state if fields don't exist.
    Works with both `adk web` and custom scripts.
    """
    state = callback_context.state
    
    # Use setdefault to avoid overwriting existing values
    state.setdefault("user_name", "Guest User")
    state.setdefault("purchased_courses", [])
    state.setdefault("interaction_history", [])
    
    # Log initialization (optional)
    if "initialized" not in state:
        state["initialized"] = True
        print(f"[CALLBACK] Initialized state for session {callback_context.session_id}")
    
    return None

# Apply callback to your agent
customer_service_agent = Agent(
    name="customer_service",
    model="gemini-2.0-flash",
    description="Customer service agent",
    instruction="""
    You are a customer service agent.
    
    User: {user_name}
    Courses: {purchased_courses}
    History: {interaction_history}
    """,
    sub_agents=[policy_agent, sales_agent, course_support_agent, order_agent],
    before_agent_callback=initialize_state_callback  # ← KEY!
)
```

### How It Works

#### With `adk web`:
1. User opens web interface
2. ADK creates empty session
3. First message triggers `before_agent_callback`
4. Callback initializes state with defaults
5. Agent has required state fields ✅

#### With Custom Script:
1. You create session with initial state
2. First message triggers `before_agent_callback`
3. `setdefault` doesn't overwrite your values
4. Agent uses your custom initial state ✅

### Benefits

✅ Agent works with `adk web` out of the box  
✅ Agent works with custom scripts  
✅ No code duplication  
✅ Consistent state structure  
✅ Easy to test both ways  

### Example Usage

```bash
# Development: Quick testing
adk web

# Production: Full control
python main.py
```

Both work perfectly! 🎉

---

## 🎯 Decision Tree

```
Do you need persistent storage?
│
├─ NO
│  │
│  ├─ Do you need custom initial state?
│  │  │
│  │  ├─ NO → Use `adk web` ✅
│  │  │
│  │  └─ YES → Use callback approach ✅
│  │
│  └─ Do you need complex conversation logic?
│     │
│     ├─ NO → Use `adk web` ✅
│     │
│     └─ YES → Write custom script ✅
│
└─ YES
   │
   └─ Need web UI?
      │
      ├─ YES → Custom script + web framework ✅
      │        (e.g., FastAPI, Streamlit)
      │
      └─ NO → Custom script with database ✅
```

---

## 💡 Practical Patterns

### Pattern 1: Development with `adk web`

**Scenario:** Building a new agent, iterating on instructions and tools.

```python
# agent.py - Simple agent definition
agent = LlmAgent(
    name="my_agent",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant.",
    tools=[my_tool]
)
```

```bash
# Terminal
adk web
```

**Result:** Instant web UI for testing. Perfect for rapid development.

---

### Pattern 2: Production with Database

**Scenario:** Deploying customer-facing application.

```python
# main.py
from google.adk.sessions import DatabaseSessionService

# Use PostgreSQL in production
db_url = "postgresql://user:pass@localhost/agentdb"
session_service = DatabaseSessionService(db_url=db_url)

# Check for existing sessions
existing_sessions = session_service.list_sessions(
    app_name="ProductionApp",
    user_id=user_id
)

if existing_sessions and len(existing_sessions.sessions) > 0:
    # Resume existing session
    session_id = existing_sessions.sessions[0].id
else:
    # Create new session with user data
    session = session_service.create_session(
        app_name="ProductionApp",
        user_id=user_id,
        state={
            "user_name": get_user_name_from_db(user_id),
            "user_tier": get_user_tier(user_id),
            "preferences": load_user_preferences(user_id)
        }
    )
    session_id = session.id

# Run agent
runner = Runner(agent=agent, app_name="ProductionApp", session_service=session_service)
# ... handle conversation
```

**Result:** Persistent sessions, user data survives restarts.

---

### Pattern 3: Hybrid for Team Development

**Scenario:** Team working on complex agent. Some use `adk web`, others use custom scripts.

```python
# agent.py - Shared agent definition with callback
def init_state(callback_context: CallbackContext):
    state = callback_context.state
    state.setdefault("user_name", "Guest")
    state.setdefault("data", [])
    return None

shared_agent = LlmAgent(
    name="team_agent",
    model="gemini-2.0-flash",
    instruction="...",
    before_agent_callback=init_state
)
```

```python
# dev_script.py - Custom script for advanced testing
from agent import shared_agent
# ... custom session management
```

```bash
# Quick testing by team members
adk web
```

**Result:** Everyone can work their way, agent works consistently.

---

### Pattern 4: Multi-User Application

**Scenario:** SaaS application with multiple customers.

```python
# app.py
async def handle_user_message(user_id: str, message: str):
    """Handle message from any user."""
    
    # Get or create session for this user
    existing = session_service.list_sessions(
        app_name="SaaSApp",
        user_id=user_id
    )
    
    if existing and len(existing.sessions) > 0:
        session_id = existing.sessions[0].id
    else:
        # New user - initialize with user-specific data
        user_data = fetch_user_data(user_id)
        session = session_service.create_session(
            app_name="SaaSApp",
            user_id=user_id,
            state={
                "user_name": user_data["name"],
                "subscription_tier": user_data["tier"],
                "usage_quota": user_data["quota"]
            }
        )
        session_id = session.id
    
    # Process message
    runner = Runner(agent=agent, app_name="SaaSApp", session_service=session_service)
    
    content = types.Content(role="user", parts=[types.Part(text=message)])
    
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    ):
        if event.is_final_response():
            return extract_response(event)
```

**Result:** Each user has isolated session with their own state.

---

## 🔍 State Initialization Strategies

### Strategy 1: No Initialization (Empty State)

**When to use:** Simple agents, no context needed.

```python
# Just define the agent
agent = LlmAgent(
    name="simple_agent",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant."
)

# Use with adk web - state starts empty
```

**Pros:** Simplest approach  
**Cons:** Agent can't reference state variables

---

### Strategy 2: Callback Initialization

**When to use:** Need defaults, want to work with both `adk web` and custom scripts.

```python
def init_callback(callback_context: CallbackContext):
    state = callback_context.state
    state.setdefault("counter", 0)
    state.setdefault("history", [])
    return None

agent = LlmAgent(
    name="callback_agent",
    model="gemini-2.0-flash",
    instruction="Counter: {counter}",
    before_agent_callback=init_callback
)
```

**Pros:** Works everywhere, consistent  
**Cons:** Defaults only, not user-specific

---

### Strategy 3: Custom Script Initialization

**When to use:** Need user-specific initial state, production deployment.

```python
# Fetch real user data
user_data = get_user_from_database(user_id)

initial_state = {
    "user_name": user_data.name,
    "user_email": user_data.email,
    "account_type": user_data.account_type,
    "preferences": user_data.preferences
}

session = session_service.create_session(
    app_name="App",
    user_id=user_id,
    state=initial_state
)
```

**Pros:** Full control, user-specific data  
**Cons:** Can't use `adk web` with this data

---

### Strategy 4: Hybrid (Best Practice)

**When to use:** Production apps that also want `adk web` compatibility.

```python
# Callback provides defaults
def init_callback(callback_context: CallbackContext):
    state = callback_context.state
    state.setdefault("user_name", "Guest")
    state.setdefault("tier", "free")
    return None

agent = LlmAgent(
    name="hybrid_agent",
    model="gemini-2.0-flash",
    instruction="User: {user_name} ({tier})",
    before_agent_callback=init_callback
)

# Custom script provides real data
if running_in_production:
    initial_state = {
        "user_name": real_user.name,
        "tier": real_user.subscription_tier
    }
    session = session_service.create_session(state=initial_state)
else:
    # adk web will use callback defaults
    pass
```

**Pros:** Works in all scenarios  
**Cons:** Slightly more complex

---

## 🚨 Common Pitfalls & Solutions

### Pitfall 1: Expecting Custom Initial State with `adk web`

❌ **Problem:**
```python
# main.py
initial_state = {"user_name": "John"}
# ...

# Then run: adk web
# Expect to see "John" in state
```

**What happens:** State is empty, "John" is ignored.

✅ **Solution:** Use callback for defaults:
```python
def init(ctx):
    ctx.state.setdefault("user_name", "John")
    return None

agent = LlmAgent(before_agent_callback=init, ...)
```

---

### Pitfall 2: Losing Data on Restart with `adk web`

❌ **Problem:**
```bash
adk web
# Chat with agent, build up state
# Close and restart
# All state is gone!
```

**What happens:** `adk web` uses `InMemorySessionService` by default.

✅ **Solution:** Use custom script with database:
```python
session_service = DatabaseSessionService(db_url="sqlite:///data.db")
```

---

### Pitfall 3: Can't Inspect State with `adk web`

❌ **Problem:**
```python
# Want to see state after each message
# But using adk web - no access to session object
```

**What happens:** No built-in state viewer in `adk web`.

✅ **Solution:** Add logging callback:
```python
def log_state(ctx):
    print(f"State: {ctx.state}")
    return None

agent = LlmAgent(after_agent_callback=log_state, ...)
```

Or use custom script for full control.

---

### Pitfall 4: Complex Logic Not Working with `adk web`

❌ **Problem:**
```python
# Need to:
# - Check database before each message
# - Update external systems
# - Custom error handling
```

**What happens:** Can't implement this with `adk web`.

✅ **Solution:** Write custom script:
```python
async for event in runner.run_async(...):
    # Custom logic here
    check_database()
    update_external_system()
    handle_errors()
```

---

## 📋 Checklist: Which Approach?

### Use `adk web` if:
- ☑️ You're in development/testing phase
- ☑️ You don't need persistent storage
- ☑️ You want instant web UI
- ☑️ Your agent logic is simple
- ☑️ You're learning ADK
- ☑️ You're doing demos

### Use Custom Script if:
- ☑️ You need database persistence
- ☑️ You have complex business logic
- ☑️ You need user-specific initial state
- ☑️ You're deploying to production
- ☑️ You need multi-user support
- ☑️ You want full control

### Use Hybrid Approach if:
- ☑️ Team uses both methods
- ☑️ You want maximum flexibility
- ☑️ You're transitioning dev → prod
- ☑️ You want easy testing

---

## 🎓 Summary

| Aspect | `adk web` | Custom Script | Hybrid |
|--------|-----------|---------------|--------|
| **Complexity** | Low | High | Medium |
| **Control** | Limited | Full | Full |
| **Setup Time** | Instant | Hours | Medium |
| **Persistence** | ❌ | ✅ | ✅ |
| **Web UI** | ✅ | ❌ | ✅ (if built) |
| **Production Ready** | ❌ | ✅ | ✅ |
| **Testing** | ✅ Perfect | ✅ Good | ✅ Perfect |

---

## 🚀 Quick Start Commands

```bash
# Development: Quick testing
adk web

# Production: Run your app
python main.py

# Production: Background service
python main.py &

# Production: With process manager
pm2 start main.py --interpreter python3
```

---

## 📚 Additional Resources

- [ADK Quick Recap](adk-quick-recap.md)
- [State Management Guide](adk-state-management-guide.md)
- [Callbacks Deep Dive](agent-vs-model-callbacks-guide.md)

---

## Key Takeaway

**`adk web` and custom scripts are complementary, not mutually exclusive.**

- Use `adk web` for **development and testing**
- Use custom scripts for **production and complex scenarios**
- Use **callbacks** to make agents work with both

Choose the right tool for the job! 🎯
