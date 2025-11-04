# Google ADK Quick Recap

A concise reference guide covering the essential concepts and patterns in the Agent Development Kit.

---

## 1. Basic Agent Setup

### Root Agent Structure
Every ADK project needs at least one **root agent** - the entry point for all interactions.

```python
from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="my_agent",              # Unique identifier (match filename)
    model="gemini-2.0-flash",     # LLM to use
    description="Brief purpose",   # Helps with task delegation
    instruction="Detailed behavior guide"
)
```

### Project Structure
```
parent_folder/
├── my_agent/
│   ├── __init__.py    # from . import agent
│   └── agent.py       # Define root_agent here
```

**Important:** Always run `adk` commands from parent folder, not inside agent folder.

---

## 2. Tools

### Tool Rules
- ❌ Cannot mix built-in tools with custom function tools in same agent
- ❌ Only one built-in tool per agent
- ✅ Multiple custom function tools per agent allowed
- 💡 For multiple tool types: create separate agents and delegate

### Custom Function Tools
```python
def get_weather(city: str, country: str) -> dict:
    """Get weather for a city.
    
    Args:
        city: Name of the city
        country: Country code (e.g., 'US', 'CA')
    """
    # Implementation
    return {"temperature": 72, "condition": "sunny"}

agent = LlmAgent(
    name="weather_agent",
    model="gemini-2.0-flash",
    tools=[get_weather]
)
```

**Best Practices:**
- ✅ Use JSON-serializable parameter types (str, int, list, dict)
- ✅ Write clear docstrings (LLM uses them!)
- ✅ Return dictionaries with descriptive keys
- ❌ Avoid default parameter values

---

## 3. Using Other LLM Models

```python
from google.adk.models import LiteLlm

model = LiteLlm(
    model="openrouter/nvidia/nemotron-nano-12b-v2-vl:free",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

root_agent = Agent(
    name="my_agent",
    model=model,  # Use custom model
    # ...
)
```

---

## 4. Structured Outputs

Force agents to return specific JSON formats using Pydantic models.

```python
from pydantic import BaseModel, Field

class CapitalOutput(BaseModel):
    capital: str = Field(description="The capital of the country")

agent = LlmAgent(
    name="capital_agent",
    instruction="Respond ONLY with JSON: {\"capital\": \"city_name\"}",
    output_schema=CapitalOutput,  # Enforce structure
    output_key="found_capital"     # Save to state
)
```

**Limitations:**
- ❌ Cannot use tools when `output_schema` is set
- ✅ LLM must directly produce JSON matching schema
- ✅ Requires explicit JSON instructions

---

## 5. Sessions, State & Runners

### State Composition
State = Session State + Event History + Metadata

```python
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()

session = await session_service.create_session(
    app_name="my_app",
    user_id="user123",
    state={"user_name": "Alice", "preferences": {}}
)
```

### Using State in Instructions
```python
agent = Agent(
    name="my_agent",
    instruction="""
    User: {user_name}
    Preferences: {user_preferences}
    """
)
```

### Runner (Executes Agent)
```python
from google.adk.runners import Runner

runner = Runner(
    agent=my_agent,
    app_name="my_app",
    session_service=session_service
)

# Execute
async for event in runner.run_async(
    user_id="user123",
    session_id="session456",
    new_message=content
):
    # Process events
```

### Session Service Types
| Type | Storage | Use Case |
|------|---------|----------|
| `InMemorySessionService` | Memory | Development/testing |
| `DatabaseSessionService` | Database | Production (persistent) |
| `VertexAISessionService` | Vertex AI | Scalable apps |

---

## 6. Persistent Storage

### Database Setup
```python
from google.adk.sessions import DatabaseSessionService

db_url = "sqlite:///./my_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)

# Check for existing sessions
existing = session_service.list_sessions(
    app_name=APP_NAME,
    user_id=USER_ID
)

if existing and len(existing.sessions) > 0:
    SESSION_ID = existing.sessions[0].id
else:
    session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state={"initial": "state"}
    )
```

### Accessing State in Tools
```python
def save_preference(key: str, value: str, tool_context: ToolContext) -> dict:
    # Read state
    current = tool_context.state.get('preferences', {})
    
    # Write state
    current[key] = value
    tool_context.state['preferences'] = current
    
    return {"status": "saved"}
```

### Running Agent Asynchronously
```python
from google.genai import types

# Create message content
content = types.Content(
    role="user",
    parts=[types.Part(text="What's the weather?")]
)

# Run and process events
async for event in runner.run_async(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=content
):
    # Check for final response
    if event.is_final_response():
        if event.content and event.content.parts:
            final_response = event.content.parts[0].text
```

---

## 7. Multi-Agent Systems

### Delegation vs Collaboration
ADK focuses on **delegation** (not collaboration like CrewAI).

### Two Patterns

#### A. Sub-Agent (Full Delegation)
Agent B takes over completely. Agent A is out of the loop.

```python
root_agent = Agent(
    name="manager",
    model="gemini-2.0-flash",
    instruction="Delegate to specialized agents...",
    sub_agents=[stock_analyst, funny_nerd]
)
```

#### B. Agent-as-Tool (Controlled)
Agent A calls Agent B, gets result, then responds to user.

```python
from google.adk.tools.agent_tool import AgentTool

root_agent = Agent(
    name="manager",
    model="gemini-2.0-flash",
    instruction="Use agents as tools...",
    tools=[
        AgentTool(news_analyst),
        get_current_time
    ]
)
```

### Key Limitation
❌ Built-in tools cannot be used in sub-agents
✅ Workaround: Use `AgentTool` wrapper or workflow agents

---

## 8. Stateful Multi-Agent Flow

```
User Question
    ↓
Session History Updated
    ↓
State Displayed (BEFORE)
    ↓
Runner → Agent
    ↓
Agent Processes (tools, thinking)
    ↓
Events Stream Back
    ↓
Events Processed & Displayed
    ↓
Final Response
    ↓
History Updated
    ↓
State Displayed (AFTER)
    ↓
Wait for Next Question
```

---

## 9. Callbacks

### Callback Types & Purposes

| Callback | When | Use For |
|----------|------|---------|
| `before_agent_callback` | Before agent starts | State setup, resource initialization |
| `after_agent_callback` | After agent completes | Cleanup, logging, state modification |
| `before_model_callback` | Before LLM call | Guardrails, dynamic instructions, caching |
| `after_model_callback` | After LLM responds | Response filtering, reformatting |
| `before_tool_callback` | Before tool executes | Authorization, arg modification, logging |
| `after_tool_callback` | After tool executes | Result modification, state updates |

### Callback Signatures

```python
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

def before_agent_callback(
    callback_context: CallbackContext
) -> Optional[types.Content]:
    # Access: agent_name, state, session_id, user_id
    pass

def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    # Access: conversation history, generation config
    pass

def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse
) -> Optional[LlmResponse]:
    # Access: model response, tool calls, usage metadata
    pass

def before_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext
) -> Optional[Dict]:
    # Access: tool name, arguments, state
    pass

def after_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
    tool_response: Dict
) -> Optional[Dict]:
    # Access: tool result, state
    pass
```

### Using Callbacks
```python
root_agent = LlmAgent(
    name="my_agent",
    model="gemini-2.0-flash",
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    tools=[my_tool],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback
)
```

### Return Types
- Return `None` → Continue normal processing
- Return object (`types.Content`, `LlmResponse`, `Dict`) → Short-circuit

### Context Objects Quick Reference

**CallbackContext** (all callbacks except tool):
- `agent_name`, `invocation_id`, `state`, `app_name`, `user_id`, `session_id`

**ToolContext** (tool callbacks):
- `agent_name`, `state`, `properties`

**LlmRequest** (before_model_callback):
- `contents`, `generation_config`, `safety_settings`, `tools`

**LlmResponse** (after_model_callback):
- `content`, `tool_calls`, `usage_metadata`

---

## 10. Sequential Agent

Executes sub-agents in **fixed order** (first to last).

```python
from google.adk.agents import SequentialAgent

root_agent = SequentialAgent(
    name="sequential_workflow",
    sub_agents=[agent1, agent2, agent3],
    description="Runs agents in order"
)
```

**Passing Data Between Agents:**
Use `output_key` to save results to state:

```python
agent1 = LlmAgent(
    name="analyzer",
    output_key="analysis_result"  # Saves to state
)

agent2 = LlmAgent(
    name="formatter",
    instruction="Format this analysis: {analysis_result}"  # Reads from state
)
```

---

## 11. Parallel Agent

Executes sub-agents **concurrently** for speed.

```python
from google.adk.agents import ParallelAgent

root_agent = ParallelAgent(
    name="parallel_workflow",
    sub_agents=[weather_agent, news_agent, stock_agent],
    description="Runs agents simultaneously"
)
```

**Key Points:**
- ✅ Dramatically faster for independent tasks
- ⚠️ Sub-agents don't share state during execution
- ✅ Results combined after all complete

---

## 12. Loop Agent

Executes sub-agents **iteratively** until condition met.

```python
from google.adk.agents import LoopAgent

refinement_loop = LoopAgent(
    name="post_refinement",
    max_iterations=10,
    sub_agents=[reviewer, refiner],
    description="Iteratively improve until quality met"
)
```

**Termination:**
- Max iterations reached (`max_iterations=10`)
- Exit condition triggered:
  ```python
  def exit_loop_tool(tool_context: ToolContext) -> dict:
      tool_context.actions.escalate = True
      return {"status": "exiting loop"}
  ```

**Use Cases:**
- Code refinement
- Content improvement
- Iterative problem solving

---

## Quick Command Reference

```bash
# Start web interface (from parent folder)
adk web

# Run agent from CLI
adk run

# Create new agent
adk create my_agent

# List available agents
adk list
```

---

## Common Patterns Cheat Sheet

### Pattern 1: Tool with State
```python
def my_tool(arg: str, tool_context: ToolContext) -> dict:
    state = tool_context.state
    result = state.get('previous_result', 'default')
    state['new_result'] = arg
    return {"result": result}
```

### Pattern 2: Agent with State Placeholders
```python
instruction = "User {user_name} wants info about {topic}"
```

### Pattern 3: Multi-Agent Delegation
```python
manager = Agent(
    sub_agents=[specialist1, specialist2],
    instruction="Delegate based on descriptions"
)
```

### Pattern 4: Sequential Workflow
```python
workflow = SequentialAgent(
    sub_agents=[
        LlmAgent(name="step1", output_key="result1"),
        LlmAgent(name="step2", instruction="Use {result1}")
    ]
)
```

### Pattern 5: Content Filtering
```python
def before_model_callback(ctx, llm_request):
    if contains_inappropriate(llm_request):
        return LlmResponse(content=blocked_message())
    return None
```

---

## Key Takeaways

1. **Root Agent Required** - Entry point for all interactions
2. **State is Persistent** - Use for session memory
3. **Tools are Functions** - Clear docstrings, dict returns
4. **Callbacks for Control** - Hook into execution flow
5. **Delegation Over Collaboration** - Sub-agents or agent-as-tool
6. **Workflow Agents** - Sequential, Parallel, Loop for complex flows
7. **Always Use Runner** - Connects agent + session + execution

---

## Additional Resources

- [State Management Guide](adk-state-management-guide.md)
- [Callbacks Deep Dive](agent-vs-model-callbacks-guide.md)
- [ADK Documentation](https://ai.google.dev/adk)

---

**Pro Tip:** Use `InMemorySessionService` for development, `DatabaseSessionService` for production!
