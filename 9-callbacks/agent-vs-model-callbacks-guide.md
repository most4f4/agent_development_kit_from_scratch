# Agent Callbacks vs Model Callbacks in Google ADK

A comprehensive guide to understanding the difference between agent-level and model-level callbacks.

---

## 🎯 The Core Confusion

**Question:** "Why do we need both agent callbacks AND model callbacks if each agent only uses one model?"

**Answer:** Because the **agent** and the **model** are conceptually different layers, and the model can be called **multiple times** within a single agent request.

---

## 🏗️ The Architecture

Think of an ADK agent as a multi-layer pipeline:

```
┌─────────────────────────────────────────────────────────┐
│                    AGENT LAYER                          │
│  (Reasoning, tool selection, session management)        │
│                                                         │
│  ┌────────────────────────────────────────────────┐     │
│  │              MODEL LAYER                       │     │
│  │  (LLM text generation - can be called N times) │     │
│  └────────────────────────────────────────────────┘     │
│                                                         │
│  ┌────────────────────────────────────────────────┐     │
│  │              TOOL LAYER                        │     │
│  │  (External function execution)                 │     │
│  └────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Comparison Table

| Aspect           | Agent Callbacks                                | Model Callbacks                                        |
| ---------------- | ---------------------------------------------- | ------------------------------------------------------ |
| **Scope**        | Entire agent invocation                        | Individual LLM calls only                              |
| **Frequency**    | **Once per user request**                      | **Multiple times per request**                         |
| **Triggers**     | When user sends message / agent completes      | Every time the LLM is called                           |
| **Access To**    | Session state, user input, final output        | Prompts, LLM responses, generation params              |
| **Typical Uses** | Request logging, analytics, session management | Prompt modification, content filtering, token tracking |
| **Level**        | High-level (orchestration)                     | Low-level (generation)                                 |

---

## 🔄 Execution Flow Example

Here's what happens when a user asks: **"What's the capital of France?"**

```
USER REQUEST: "What's the capital of France?"
│
├─ 🟦 BEFORE_AGENT_CALLBACK (fires once)
│   ├─ Log: "Request #1 started"
│   ├─ Initialize session state
│   └─ Record timestamp
│
├─ Agent starts processing...
│
│   ├─ 🟩 BEFORE_MODEL_CALLBACK (1st call)
│   │   ├─ Prompt: "User asks: What's the capital of France?"
│   │   └─ Log: "Sending prompt to LLM"
│   │
│   ├─ 💬 MODEL GENERATES (1st call)
│   │   └─ Output: "I'll use the get_capital_city tool"
│   │
│   ├─ 🟩 AFTER_MODEL_CALLBACK (1st call)
│   │   ├─ Response: Function call decision
│   │   └─ Log: "Model chose to use tool"
│   │
│   ├─ 🔧 TOOL EXECUTES
│   │   └─ get_capital_city("France") → "Paris"
│   │
│   ├─ 🟩 BEFORE_MODEL_CALLBACK (2nd call)
│   │   ├─ Prompt: "Tool returned: Paris. Format final answer."
│   │   └─ Log: "Sending tool results to LLM"
│   │
│   ├─ 💬 MODEL GENERATES (2nd call)
│   │   └─ Output: "The capital of France is Paris."
│   │
│   └─ 🟩 AFTER_MODEL_CALLBACK (2nd call)
│       ├─ Response: Final formatted answer
│       └─ Log: "Model generated final response"
│
└─ 🟦 AFTER_AGENT_CALLBACK (fires once)
    ├─ Log: "Request #1 completed"
    ├─ Calculate duration
    └─ Update analytics

FINAL OUTPUT: "The capital of France is Paris."
```

**Summary:**

- **Agent callbacks**: 2 total (1 before + 1 after)
- **Model callbacks**: 4 total (2 before + 2 after)

---

## 🎯 When to Use Each

### Use **Agent Callbacks** for:

✅ **Session Management**

```python
def before_agent_callback(callback_context):
    state = callback_context.state
    if "user_id" not in state:
        state["user_id"] = generate_user_id()
    return None
```

✅ **Request-Level Logging**

```python
def after_agent_callback(callback_context):
    log_to_database({
        "request_id": callback_context.state.get("request_id"),
        "duration": calculate_duration(),
        "user_message": callback_context.state.get("user_message")
    })
    return None
```

✅ **High-Level Analytics**

- Track total requests per user
- Measure end-to-end response time
- Count successful vs failed requests

✅ **Access Control**

```python
def before_agent_callback(callback_context):
    if not user_has_permission(callback_context.state.get("user_id")):
        return types.Content(
            role="model",
            parts=[types.Part(text="Access denied.")]
        )
    return None
```

---

### Use **Model Callbacks** for:

✅ **Content Filtering**

```python
def before_model_callback(callback_context, llm_request):
    user_message = extract_user_message(llm_request)
    if contains_profanity(user_message):
        return LlmResponse(content=create_blocked_message())
    return None
```

✅ **Prompt Engineering**

```python
def before_model_callback(callback_context, llm_request):
    # Inject dynamic system instructions
    llm_request.system_instruction = f"Current time: {datetime.now()}"
    return None
```

✅ **Response Transformation**

```python
def after_model_callback(callback_context, llm_response):
    # Replace negative words with positive alternatives
    text = llm_response.content.parts[0].text
    text = text.replace("problem", "challenge")
    return modified_response(text)
```

✅ **Token/Cost Tracking**

```python
def after_model_callback(callback_context, llm_response):
    track_usage(
        prompt_tokens=llm_response.usage.prompt_tokens,
        completion_tokens=llm_response.usage.completion_tokens,
        cost=calculate_cost(llm_response.usage)
    )
    return None
```

✅ **A/B Testing Prompts**

- Test different system instructions
- Compare model parameters
- Measure generation quality

---

## 💡 Real-World Scenarios

### Scenario 1: Customer Support Bot

```python
# AGENT CALLBACK - Track customer sessions
def before_agent_callback(callback_context):
    state = callback_context.state
    state["session_start"] = datetime.now()
    state["customer_id"] = extract_customer_id()
    log_session_start(state["customer_id"])
    return None

# MODEL CALLBACK - Filter sensitive info from responses
def after_model_callback(callback_context, llm_response):
    text = llm_response.content.parts[0].text
    text = redact_credit_cards(text)
    text = redact_ssn(text)
    return modified_response(text)
```

**Why both?**

- Agent callback handles the **session lifecycle**
- Model callback handles **every individual LLM generation** (which happens multiple times)

---

### Scenario 2: Research Assistant with Tools

```python
# AGENT CALLBACK - Track research queries
def before_agent_callback(callback_context):
    state = callback_context.state
    state["research_query"] = extract_user_query()
    state["tools_used"] = []
    return None

# MODEL CALLBACK - Count LLM calls and tokens
def after_model_callback(callback_context, llm_response):
    state = callback_context.state
    state.setdefault("llm_call_count", 0)
    state["llm_call_count"] += 1
    state.setdefault("total_tokens", 0)
    state["total_tokens"] += llm_response.usage.total_tokens
    return None
```

**Result:** For a single research query that uses 3 tools:

- Agent callbacks fire: **2 times** (start and end)
- Model callbacks fire: **8+ times** (multiple reasoning steps)
- You get accurate per-query token counts!

---

## 🚨 Common Misconceptions

### ❌ Misconception 1

> "Since my agent uses one model, agent callbacks and model callbacks are the same."

**Reality:** The model gets called **multiple times** per agent request, especially when tools are involved.

---

### ❌ Misconception 2

> "I should use model callbacks for session management."

**Reality:** Session state should be managed at the agent level. Model callbacks might run 10+ times in a complex request!

---

### ❌ Misconception 3

> "I can modify the final response in agent callbacks."

**Reality:** Agent callbacks see the complete flow, but model callbacks are better for transforming LLM outputs since they catch **each generation**.

---

## 🔍 Debugging: See The Difference

Add this to your agent to see when callbacks fire:

```python
def before_agent_callback(callback_context):
    print("=" * 50)
    print("🟦 AGENT START")
    print("=" * 50)
    return None

def before_model_callback(callback_context, llm_request):
    print("  🟩 MODEL CALL START")
    return None

def after_model_callback(callback_context, llm_response):
    print("  🟩 MODEL CALL END")
    return None

def after_agent_callback(callback_context):
    print("=" * 50)
    print("🟦 AGENT END")
    print("=" * 50)
    return None
```

**Output for a tool-using query:**

```
==================================================
🟦 AGENT START
==================================================
  🟩 MODEL CALL START
  🟩 MODEL CALL END
  [Tool execution]
  🟩 MODEL CALL START
  🟩 MODEL CALL END
==================================================
🟦 AGENT END
==================================================
```

---

## 📋 Quick Decision Guide

**Start here:** What do you need to do?

```
Do I need to...
│
├─ Track/modify the USER REQUEST or FINAL RESPONSE?
│  └─ ✅ Use AGENT callbacks
│
├─ Track/modify EVERY LLM INTERACTION?
│  └─ ✅ Use MODEL callbacks
│
├─ Manage SESSION STATE or USER CONTEXT?
│  └─ ✅ Use AGENT callbacks
│
├─ Filter/transform GENERATED TEXT?
│  └─ ✅ Use MODEL callbacks
│
├─ Count TOKENS or track COSTS?
│  └─ ✅ Use MODEL callbacks
│
├─ Implement RATE LIMITING per user?
│  └─ ✅ Use AGENT callbacks
│
└─ Inject DYNAMIC PROMPTS or SYSTEM INSTRUCTIONS?
   └─ ✅ Use MODEL callbacks
```

---

## 🎓 Key Takeaways

1. **Agent = Orchestrator**, Model = Generator
2. **One agent request** = One agent callback pair
3. **One agent request** = Multiple model callback pairs (often 2-10+)
4. Agent callbacks wrap **everything** (including all model calls)
5. Model callbacks wrap **individual LLM generations**
6. Use agent callbacks for **request-level concerns**
7. Use model callbacks for **generation-level concerns**

---

## 📚 Additional Resources

- [Google ADK Callbacks Documentation](https://ai.google.dev/adk)
- Code Examples: `9-callbacks/before_after_agent/`, `9-callbacks/before_after_model/`
- Tool Callbacks: `9-callbacks/before_after_tool/`

---

**Questions?** Remember: When in doubt, think about **frequency**. If it should happen once per user message, use agent callbacks. If it should happen every time the LLM generates text, use model callbacks.
