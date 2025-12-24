import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

from langchain_openai import ChatOpenAI

load_dotenv()

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Define simple tools

@tool
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    Supports +, -, *, /, **, (), etc.
    Example: '2 + 2 * 3' or '(10 + 5) / 3'
    """
    try:
        # Safe evaluation of math expressions
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_word_length(word: str) -> str:
    """
    Get the length of a word or phrase.
    Example: 'Hello' returns 5
    """
    return f"The length of '{word}' is {len(word)} characters"


@tool
def reverse_text(text: str) -> str:
    """
    Reverse a string of text.
    Example: 'Hello' becomes 'olleH'
    """
    return f"Reversed: {text[::-1]}"


async def streaming_multi_step_agent():
    """
    Demonstrates LangChain agent making MULTIPLE tool calls with streaming.
    Watch as the agent thinks, calls tools, and synthesizes results in real-time!
    """
    
    # Initialize model with OpenRouter
    model = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        model="nvidia/nemotron-3-nano-30b-a3b:free",
        temperature=0,
        streaming=True  # Enable streaming
    )
    
    # Define available tools
    tools = [calculator, get_word_length, reverse_text]
    
    print("🤖 Multi-Step Streaming Agent Ready!\n")
    print("Available tools:")
    for t in tools:
        print(f"  • {t.name}: {t.description}")
    
    print("\n📝 Try multi-step queries like:")
    print("  • 'Calculate 15 * 23, then find the length of the result'")
    print("  • 'What is 100 divided by 4, then multiply by 3'")
    print("  • 'Reverse the word Python, then tell me its length'")
    print("  • 'Calculate (45 + 55) * 2, reverse it, then get its length'")
    print("\nType 'quit' to exit.\n")
    print("=" * 70)
    
    # System prompt to allow agent to use LLM knowledge when tools aren't needed
    system_prompt = """You are a helpful AI assistant with access to tools.

IMPORTANT INSTRUCTIONS:
1. If a user's question can be answered using your available tools, USE THEM.
2. If NO tool is applicable, answer the question using your own knowledge directly.
3. Do NOT refuse to answer just because no tool is available - use your knowledge!
4. For factual questions (dates, locations, general knowledge), answer directly from your knowledge.
5. Only use tools when they are genuinely needed for the task.
"""
    
    # Create ReAct agent with state_modifier for custom system prompt
    agent = create_agent(model, tools=tools, system_prompt=system_prompt)
    
    while True:
        user_input = input("\n💬 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        print("\n🧠 Agent working...\n")
        
        try:
            step_number = 0
            tool_call_count = 0
            
            # Stream through agent events
            async for event in agent.astream(
                {"messages": [{"role": "user", "content": user_input}]},
                stream_mode="values"
            ):
                messages = event.get("messages", [])
                if not messages:
                    continue
                
                last_message = messages[-1]
                
                # Agent is planning to use tools
                if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                    for tool_call in last_message.tool_calls:
                        tool_call_count += 1
                        tool_name = tool_call.get("name", "unknown")
                        tool_args = tool_call.get("args", {})
                        
                        print(f"🔧 Tool Call #{tool_call_count}: {tool_name}")
                        
                        # Show what the agent is passing to the tool
                        for key, value in tool_args.items():
                            print(f"   └─ {key}: {value}")
                
                # Tool execution completed
                if last_message.type == "tool":
                    step_number += 1
                    print(f"\n✅ Step {step_number} Complete: {last_message.name}")
                    print(f"   └─ Output: {last_message.content}")
                    print()
                
                # Agent's final reasoning and answer
                if last_message.type == "ai" and last_message.content:
                    # Check if this is the final answer (no more tool calls)
                    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
                        print(f"💡 Agent's Reasoning & Answer:")
                        print(f"   {last_message.content}")
                        print(f"\n📊 Summary: Used {tool_call_count} tool call(s) across {step_number} step(s)")
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n⚠️  Set OPENROUTER_API_KEY before running!")
    print("Get your key at: https://openrouter.ai/keys\n")
    asyncio.run(streaming_multi_step_agent())