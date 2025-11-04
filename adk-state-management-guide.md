# State Management in Google ADK

A comprehensive guide to understanding how different components access and update state information in the Agent Development Kit.

---

## 🎯 What is State?

**State** in ADK is a persistent dictionary that stores information across a conversation session. It enables:

- Context preservation between messages
- Data sharing between tools and agents
- Session-specific customization
- Multi-turn conversation memory

**Key Concept:** State is tied to a `session_id` and persists throughout the conversation lifecycle.

---

## 🏗️ State Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                       AGENT                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              STATE (dict)                            │  │
│  │  {                                                   │  │
│  │    "user_id": "123",                                 │  │
│  │    "conversation_count": 5,                          │  │
│  │    "last_topic": "weather"                           │  │
│  │  }                                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  * Reads via: {key}                                        │
│  * Writes via: output_key                                  │
└────┬────────────────────────┬───────────────────────┬──────┘
     │                        │                       │
     ▼                        ▼                       ▼
┌─────────┐           ┌──────────────┐       ┌──────────────┐
│  TOOLS  │           │  CALLBACKS   │       │   MEMORY     │
│         │           │              │       │ (if enabled) │
│ Read: ✅│           │  Read: ✅   │       │ Read: ✅     │
│ Write:✅│           │  Write: ⚠️  │       │  Write: ✅   │
│         │           │              │       │              │
│ via     │           │  via         │       │  via         │
│ Tool    │           │  Callback    │       │  Agent API   │
│ Context │           │  Context     │       │              │
└─────────┘           └──────────────┘       └──────────────┘
```

---

## 📊 Component Access Matrix

| Component             | Read State  | Write State        | Access Method             | Primary Purpose                 |
| --------------------- | ----------- | ------------------ | ------------------------- | ------------------------------- |
| **Agent**             | ✅ Full     | ✅ Full            | `{key}`, `output_key`     | Owns and orchestrates state     |
| **Tools**             | ✅ Full     | ✅ Full            | `ToolContext`             | Execute operations with context |
| **Callbacks (Agent)** | ✅ Full     | ✅ Direct          | `CallbackContext.state`   | Session management, logging     |
| **Callbacks (Model)** | ✅ Full     | ✅ Direct          | `CallbackContext.state`   | Request tracking, filtering     |
| **Callbacks (Tool)**  | ✅ Full     | ✅ Via ToolContext | `ToolContext` in callback | Tool monitoring, modification   |
| **Session Service**   | ✅ Full     | ✅ Full            | Direct API                | Low-level persistence           |
| **Memory**            | ✅ Indirect | ✅ Indirect        | Through Agent             | Long-term context (if enabled)  |

---

## 🔍 Detailed Component Breakdown

### 1️⃣ Agent (Primary State Owner)

**Access Level:** ✅ Full Read/Write

The agent is the **central controller** of state. It manages state through:

#### **Declarative Access (Recommended)**

**Reading State:**

```python
agent = LlmAgent(
    name="my_agent",
    instruction="""
    You are assisting {user_name}.
    They have {request_count} previous requests.
    Their preferred language is {language}.
    """
)
```

**Writing State:**

```python
# Using output_key to store tool results
agent = LlmAgent(
    name="weather_agent",
    tools=[get_weather],
    output_key="weather_data"
)
```

#### **Programmatic Access**

State is automatically managed by the agent runtime, but you can initialize it:

```python
# When sending messages (using ADK's session management)
response = agent.send_message(
    user_message="What's the weather?",
    session_id="user_123"  # State tied to this session
)
```

**Key Points:**

- Agent state is persistent across the conversation
- Uses `{key}` syntax for reading state variables
- Uses `output_key` in tool definitions to write results
- State is automatically passed to LLM prompts when using `{key}`

---

### 2️⃣ Tools (Full State Access)

**Access Level:** ✅ Full Read/Write via `ToolContext`

Tools can both read and modify state through the `ToolContext` parameter.

#### **Reading State in Tools**

```python
from google.adk.tools.tool_context import ToolContext

def personalized_greeting(name: str, tool_context: ToolContext) -> dict:
    """Greet user with personalized message."""

    # Read current state
    state = tool_context.state

    visit_count = state.get("visit_count", 0)
    last_visit = state.get("last_visit", "never")

    greeting = f"Hello {name}! Visit #{visit_count}. Last seen: {last_visit}"

    return {"greeting": greeting}
```

#### **Writing State in Tools**

```python
def track_user_activity(action: str, tool_context: ToolContext) -> dict:
    """Track user actions in state."""

    # Get current state
    state = tool_context.state

    # Update state directly
    state["last_action"] = action
    state["action_count"] = state.get("action_count", 0) + 1
    state["last_activity_time"] = datetime.now().isoformat()

    # Add to activity history
    if "activity_history" not in state:
        state["activity_history"] = []
    state["activity_history"].append({
        "action": action,
        "timestamp": datetime.now().isoformat()
    })

    return {"status": "tracked", "total_actions": state["action_count"]}
```

**Important Notes:**

- Changes to `tool_context.state` are **automatically persisted**
- State modifications are immediately available to subsequent tools/agent
- Tools share the same state dictionary as the agent

---

### 3️⃣ Callbacks (State Access Varies by Type)

#### **A. Agent Callbacks**

**Access Level:** ✅ Full Read, ✅ Full Write (Direct)

Agent callbacks have **direct access** to state and can modify it freely:

```python
from google.adk.agents.callback_context import CallbackContext

def before_agent_callback(callback_context: CallbackContext):
    """Initialize session state before agent runs."""

    state = callback_context.state

    # READ state
    user_id = state.get("user_id")

    # WRITE state directly
    if "session_start" not in state:
        state["session_start"] = datetime.now().isoformat()

    state["request_count"] = state.get("request_count", 0) + 1

    # Add session metadata
    state["agent_name"] = callback_context.agent_name

    return None

def after_agent_callback(callback_context: CallbackContext):
    """Update state after agent completes."""

    state = callback_context.state

    # WRITE state
    state["last_response_time"] = datetime.now().isoformat()
    state["session_active"] = True

    return None
```

**Key Points:**

- Direct dictionary access: `state["key"] = value`
- Changes are **automatically persisted**
- Perfect for session initialization and cleanup

---

#### **B. Model Callbacks**

**Access Level:** ✅ Full Read, ✅ Full Write (Direct)

Model callbacks also have direct state access:

```python
def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest
):
    """Track model calls in state."""

    state = callback_context.state

    # WRITE state
    state["model_call_count"] = state.get("model_call_count", 0) + 1
    state["last_model_call"] = datetime.now().isoformat()

    return None

def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse
):
    """Track token usage in state."""

    state = callback_context.state

    # WRITE state
    total_tokens = state.get("total_tokens", 0)
    state["total_tokens"] = total_tokens + llm_response.usage.total_tokens

    return None
```

---

#### **C. Tool Callbacks**

**Access Level:** ✅ Read via ToolContext, ✅ Write via ToolContext

Tool callbacks receive `ToolContext` which provides state access:

```python
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

def before_tool_callback(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext
):
    """Log tool usage in state."""

    state = tool_context.state

    # READ state
    tools_used = state.get("tools_used", [])

    # WRITE state
    tools_used.append({
        "tool": tool.name,
        "args": args,
        "timestamp": datetime.now().isoformat()
    })
    state["tools_used"] = tools_used

    return None

def after_tool_callback(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
    tool_response: dict
):
    """Track successful tool executions."""

    state = tool_context.state

    # WRITE state
    state["last_successful_tool"] = tool.name
    state["tool_success_count"] = state.get("tool_success_count", 0) + 1

    return None
```

---

### 4️⃣ Memory (Advanced Feature)

**Access Level:** ✅ Indirect Read/Write through Agent

⚠️ **Note:** Memory is an advanced feature that may not be available in all ADK versions.

Memory components can store and retrieve context beyond the immediate session state:

```python
# Conceptual example (API may vary)
agent = LlmAgent(
    name="memory_agent",
    memory=MemoryConfig(
        enabled=True,
        max_tokens=10000,
        summarization=True
    )
)
```

**What Memory Does:**

- Stores conversation history beyond current session
- Can summarize long conversations
- Provides semantic search over past interactions
- Complements state (doesn't replace it)

**State vs Memory:**
| Feature | State | Memory |
|---------|-------|--------|
| Scope | Current session | Cross-session |
| Structure | Dictionary | Conversation history |
| Access | Direct | Through agent APIs |
| Purpose | Immediate context | Long-term context |

---

## 🔄 State Lifecycle

### Complete Request Flow with State Updates

```
1. USER SENDS MESSAGE
   ↓
2. BEFORE_AGENT_CALLBACK
   ├─ state["request_count"] += 1
   ├─ state["request_start"] = now()
   └─ Log request
   ↓
3. AGENT PROCESSES (reads state via {key})
   ├─ Instruction: "User {user_name} has {request_count} requests"
   └─ State values injected into prompt
   ↓
4. BEFORE_MODEL_CALLBACK
   ├─ state["model_call_count"] += 1
   └─ Log model call
   ↓
5. MODEL GENERATES
   └─ Decides to use tool
   ↓
6. AFTER_MODEL_CALLBACK
   └─ Log model response
   ↓
7. BEFORE_TOOL_CALLBACK
   ├─ state["tools_used"].append(tool_name)
   └─ Log tool invocation
   ↓
8. TOOL EXECUTES
   ├─ tool_context.state["last_weather"] = result
   └─ Tool modifies state
   ↓
9. AFTER_TOOL_CALLBACK
   ├─ state["tool_success_count"] += 1
   └─ Log completion
   ↓
10. BEFORE_MODEL_CALLBACK (2nd call)
    └─ state["model_call_count"] += 1
    ↓
11. MODEL GENERATES FINAL RESPONSE
    └─ Uses tool result
    ↓
12. AFTER_MODEL_CALLBACK (2nd call)
    └─ Log final response
    ↓
13. AFTER_AGENT_CALLBACK
    ├─ duration = now() - state["request_start"]
    ├─ state["last_response"] = response
    └─ Log completion
    ↓
14. STATE PERSISTED TO SESSION SERVICE
    └─ All changes saved
```

---

## 💡 Practical Examples

### Example 1: User Session Tracking

```python
def before_agent_callback(callback_context: CallbackContext):
    """Initialize and track user session."""
    state = callback_context.state

    # First-time user setup
    if "user_initialized" not in state:
        state["user_initialized"] = True
        state["session_count"] = 1
        state["first_seen"] = datetime.now().isoformat()
        state["preferences"] = {
            "language": "en",
            "timezone": "UTC"
        }
    else:
        state["session_count"] += 1

    state["last_seen"] = datetime.now().isoformat()

    return None
```

---

### Example 2: Tool with State Persistence

```python
def save_user_preference(
    preference_key: str,
    preference_value: str,
    tool_context: ToolContext
) -> dict:
    """Save user preference to state."""

    state = tool_context.state

    # Initialize preferences dict if not exists
    if "user_preferences" not in state:
        state["user_preferences"] = {}

    # Save preference
    state["user_preferences"][preference_key] = preference_value
    state["last_preference_update"] = datetime.now().isoformat()

    return {
        "status": "saved",
        "key": preference_key,
        "value": preference_value
    }

# Usage in agent
agent = LlmAgent(
    name="preference_agent",
    instruction="""
    User's current preferences: {user_preferences}

    When user sets a preference, use save_user_preference tool.
    """,
    tools=[save_user_preference]
)
```

---

### Example 3: Tracking Conversation Topics

```python
def before_agent_callback(callback_context: CallbackContext):
    """Track conversation topics."""
    state = callback_context.state

    # Initialize topic tracking
    if "conversation_topics" not in state:
        state["conversation_topics"] = []

    return None

def after_agent_callback(callback_context: CallbackContext):
    """Extract and save topic from conversation."""
    state = callback_context.state

    # Hypothetical: extract topic from last interaction
    # In real implementation, you might analyze the conversation
    current_topic = extract_topic_from_conversation()

    topics = state["conversation_topics"]
    if current_topic and current_topic not in topics[-5:]:  # Keep last 5 unique
        topics.append(current_topic)
        state["conversation_topics"] = topics[-10:]  # Keep max 10

    return None
```

---

### Example 4: Multi-Tool Workflow with State

```python
def search_products(query: str, tool_context: ToolContext) -> dict:
    """Search for products and save to state."""
    state = tool_context.state

    # Perform search
    results = perform_product_search(query)

    # Save to state for next tool
    state["search_results"] = results
    state["search_query"] = query

    return {"results": results, "count": len(results)}

def filter_products(
    max_price: float,
    category: str,
    tool_context: ToolContext
) -> dict:
    """Filter previously searched products from state."""
    state = tool_context.state

    # Get previous search results from state
    search_results = state.get("search_results", [])

    # Apply filters
    filtered = [
        p for p in search_results
        if p["price"] <= max_price and p["category"] == category
    ]

    # Save filtered results
    state["filtered_results"] = filtered

    return {"filtered_results": filtered, "count": len(filtered)}

# Agent can chain these tools, sharing state
agent = LlmAgent(
    name="shopping_agent",
    instruction="""
    First search_products, then filter_products.
    Results are automatically shared via state.
    """,
    tools=[search_products, filter_products]
)
```

---

## 🚨 Common Patterns and Best Practices

### ✅ DO: Use State for Session Data

```python
# Good: Track user-specific session info
state["user_id"] = "user_123"
state["session_start"] = datetime.now().isoformat()
state["preferences"] = {"theme": "dark"}
```

### ✅ DO: Use State to Share Data Between Tools

```python
# Tool 1: Fetch data
def fetch_data(tool_context: ToolContext):
    data = api_call()
    tool_context.state["fetched_data"] = data
    return {"status": "fetched"}

# Tool 2: Process data from state
def process_data(tool_context: ToolContext):
    data = tool_context.state.get("fetched_data")
    processed = transform(data)
    return {"result": processed}
```

### ✅ DO: Initialize State in Agent Callbacks

```python
def before_agent_callback(callback_context: CallbackContext):
    state = callback_context.state

    # Initialize required keys
    if "request_counter" not in state:
        state["request_counter"] = 0
        state["user_preferences"] = {}
        state["history"] = []

    return None
```

### ❌ DON'T: Store Large Objects in State

```python
# Bad: State should be JSON-serializable and reasonably sized
state["entire_database"] = huge_dataset  # ❌

# Good: Store references or summaries
state["dataset_id"] = "dataset_123"  # ✅
state["dataset_summary"] = {"rows": 1000, "columns": 50}  # ✅
```

### ❌ DON'T: Use State for Temporary Computation

```python
# Bad: Using state as scratch space
def compute_something(tool_context: ToolContext):
    state = tool_context.state
    state["temp_value_1"] = x * 2  # ❌
    state["temp_value_2"] = y + 3  # ❌
    result = state["temp_value_1"] + state["temp_value_2"]
    return result

# Good: Use local variables
def compute_something(tool_context: ToolContext):
    temp1 = x * 2  # ✅
    temp2 = y + 3  # ✅
    result = temp1 + temp2
    return result
```

### ✅ DO: Use Nested Structures

```python
# Good: Organize related data
state["user"] = {
    "id": "123",
    "name": "Alice",
    "preferences": {
        "language": "en",
        "timezone": "PST"
    }
}

# Access in instructions
instruction = """
User name: {user[name]}
User language: {user[preferences][language]}
"""
```

---

## 🎯 State vs Other Storage

### When to Use State vs Database

| Use State When                    | Use Database When           |
| --------------------------------- | --------------------------- |
| Data needed during session        | Data needed across sessions |
| Temporary context                 | Permanent records           |
| User preferences for current chat | Historical user data        |
| Tool outputs for current request  | Analytics and reporting     |
| < 100KB of data                   | Large datasets              |

### Example: Hybrid Approach

```python
def save_chat_summary(
    summary: str,
    tool_context: ToolContext
) -> dict:
    """Save to both state (temporary) and database (permanent)."""

    state = tool_context.state

    # Save to state for current session
    state["current_summary"] = summary

    # Save to database for long-term storage
    user_id = state.get("user_id")
    save_to_database(user_id, summary, timestamp=datetime.now())

    return {"status": "saved to both state and database"}
```

---

## 🔐 Security Considerations

### Sanitize State Data

```python
def before_agent_callback(callback_context: CallbackContext):
    state = callback_context.state

    # Remove sensitive data before logging
    safe_state = {k: v for k, v in state.items()
                  if k not in ["password", "api_key", "token"]}

    logger.info(f"State: {safe_state}")

    return None
```

### Validate State Access

```python
def sensitive_operation(user_role: str, tool_context: ToolContext) -> dict:
    state = tool_context.state

    # Check permissions from state
    if state.get("user_role") != "admin":
        return {"error": "Insufficient permissions"}

    # Proceed with operation
    return perform_sensitive_operation()
```

---

## 📚 Quick Reference

### State Access Cheatsheet

```python
# In Agent Callbacks
state = callback_context.state
state["key"] = "value"  # Direct write ✅

# In Model Callbacks
state = callback_context.state
state["key"] = "value"  # Direct write ✅

# In Tool Callbacks
state = tool_context.state
state["key"] = "value"  # Write via ToolContext ✅

# In Tools
state = tool_context.state
state["key"] = "value"  # Direct write ✅

# In Agent Instructions (declarative)
instruction = "User name is {user_name}"  # Read only ✅

# In Agent Tool Definitions
# output_key="result"  # Write only ✅
```

---

## 🎓 Key Takeaways

1. **State is Session-Scoped**: Tied to `session_id`, persists across conversation
2. **Agent Owns State**: Primary controller and orchestrator
3. **Tools Have Full Access**: Can read and write via `ToolContext`
4. **Callbacks Can Modify**: All callback types have direct state access
5. **Declarative is Preferred**: Use `{key}` and `output_key` in agents when possible
6. **State is Persistent**: Changes are automatically saved
7. **Keep State Lean**: Store only session-relevant data
8. **Use for Coordination**: Perfect for sharing data between tools and tracking session info

---

## 🔗 Related Documentation

- Agent Callbacks: See `agent-vs-model-callbacks-guide.md`
- Tool Development: See ADK Tools documentation
- Session Management: See ADK Session Service docs

---

**Remember:** State is your agent's memory for the current conversation. Use it wisely to create stateful, context-aware interactions!
