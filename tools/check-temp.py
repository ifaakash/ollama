import ollama

# Define the tool as a standard Python function
# The type hints and docstring are CRITICAL. Ollama reads them to 
# explain to the LLM what this tool does and when to use it.
def get_pi_temperature() -> str:
    """
    Get the current CPU temperature of the Raspberry Pi hardware.
    
    Returns:
        str: The current temperature in Celsius.
    """
    try:
        # The standard hardware file where the Pi OS stores thermal data
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_millicelsius = int(f.read().strip())
            temp_celsius = temp_millicelsius / 1000.0
            return f"{temp_celsius}°C"
    except Exception as e:
        return f"Error reading system temperature: {str(e)}"

# 2. Setup the initial context window
messages = [
    {
        "role": "system",
        "content": "You are an SRE assistant running locally on a Raspberry Pi. You have access to system diagnostic tools."
    },
    {
        "role": "user",
        "content": "Hey, is the system running hot right now? Check the hardware temperature for me."
    }
]

# 3. Make the initial call to the local model
# We pass our Python function directly into the 'tools' array
# Note: Ensure you are using a model that supports tool calling, like llama3.1 or qwen2.5-coder
model_name = "qwen2.5:1.5b"

print(">> Sending prompt to LLM...")
response = ollama.chat(
    model=model_name,
    messages=messages,
    tools=[get_pi_temperature] 
)

print(">> Output response from Ollama...")
print(response)

# Append the model's internal thought process/tool request to the context window
messages.append(response.message)

# 4. Check if the model decided to invoke a tool
if response.message.tool_calls:
    print(">> The LLM decided to use a tool!")
    
    for tool_call in response.message.tool_calls:
        # Check which function the LLM wants to execute
        if tool_call.function.name == "get_pi_temperature":
            print(">> Executing get_pi_temperature() locally...")
            
            # Execute the actual Python code
            actual_temp = get_pi_temperature()
            print(f">> Tool Result: {actual_temp}")
            
            # 5. Send the real-world result back to the LLM
            messages.append({
                "role": "tool",
                "content": actual_temp,
                "name": tool_call.function.name
            })
            
    # Generate the final human-readable response
    print(">> Asking LLM to interpret the results...\n")
    final_response = ollama.chat(
        model=model_name,
        messages=messages
    )
    print("--- Final AI Response ---")
    print(final_response.message.content)

else:
    # If the model didn't use a tool, it just responds normally
    print(">> The model answered directly without using a tool.\n")
    print(response.message.content)
