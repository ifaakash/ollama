# Multi-Tool Calling Nuances with Ollama

When implementing multi-tool calling with local LLMs, several Python and Ollama-specific patterns are critical for reliability.

---

## 1. Structure of `response.message.tool_calls`

When the LLM decides to call tools, `response.message.tool_calls` is a **list of `ToolCall` objects**. 
Even if the model only calls a single tool, it is still a list containing one element.

```python
# response.message.tool_calls is structured like this:
[
    ToolCall(
        function=Function(
            name='get_cpu_temp', 
            arguments={'username': 'dev_user'}
        )
    ),
    ToolCall(
        function=Function(
            name='get_fan_speed', 
            arguments={'username': 'dev_user'}
        )
    )
]
```

To access the properties safely:
- **Function Name**: `tool_call.function.name`
- **Function Arguments**: `tool_call.function.arguments` (this is a parsed Python dictionary, e.g. `{'username': 'dev_user'}`)

---

## 2. Dynamic Execution with `**func_args`

Instead of manually extracting parameters (e.g. `username = func_args['username']`), you can use Python's double-asterisk operator `**` to unpack the arguments dictionary directly into your local function:

```python
# If the function is defined as:
def get_cpu_temp(username: str):
    ...

# And func_args is {'username': 'dev_user'}:
result = available_tools[func_name](**func_args)

# This is equivalent to calling:
result = get_cpu_temp(username='dev_user')
```

### Safety Tip: Unexpected Arguments
Sometimes, local models might hallucinate and pass extra arguments that your Python function doesn't expect. To prevent your code from crashing, you can use Python's standard parameter expansion `*args` and `**kwargs` in your function definitions, or inspect arguments beforehand:

```python
# Safe definition that won't crash on extra arguments
def get_cpu_temp(username: str, **kwargs) -> str:
    # Any unexpected arguments get captured by kwargs and ignored
    ...
```

---

## 3. The Conversation Timeline order

Ollama enforces a strict order for message history during a tool-calling lifecycle. If this sequence is violated, Ollama will raise an error.

The correct message sequence in the list must be:
1. `{'role': 'user', 'content': '...'}` (Initial prompt)
2. `response.message` (The LLM response requesting the tool calls)
3. `{'role': 'tool', 'name': 'tool_1', 'content': '...'}` (First tool result)
4. `{'role': 'tool', 'name': 'tool_2', 'content': '...'}` (Second tool result)
5. *(Optional subsequent User prompt or instructions)*

> **Rule of thumb:** Every single requested tool call in `response.message.tool_calls` **must** have a corresponding `'role': 'tool'` message returned in the next history list, matching the requested `name`.
