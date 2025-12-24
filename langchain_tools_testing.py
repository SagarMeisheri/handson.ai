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
#     system_prompt = """You are a helpful AI assistant with access to tools.

# IMPORTANT INSTRUCTIONS:
# 1. If a user's question can be answered using your available tools, USE THEM.
# 2. If NO tool is applicable, answer the question using your own knowledge directly.
# 3. Do NOT refuse to answer just because no tool is available - use your knowledge!
# 4. For factual questions (dates, locations, general knowledge), answer directly from your knowledge.
# 5. Only use tools when they are genuinely needed for the task.
# """

        # System prompt to enforce ONLY tool use for answering questions
    system_prompt = """You are a precise AI assistant that ONLY answers using tools.

STRICT RULES:
1. You MUST use tools for EVERY part of your response. Never compute or reason without tools.
2. For ANY calculation (addition, multiplication, etc.) - use the calculator tool.
3. For ANY text length question - use the get_word_length tool.
4. For ANY text reversal - use the reverse_text tool.
5. If a question requires multiple operations, break it down and use tools for EACH step.
6. Do NOT perform mental math or estimate - ALWAYS call the calculator.
7. Do NOT count characters yourself - ALWAYS call get_word_length.
8. Show your work by calling tools step-by-step, then synthesize the final answer.

If a question cannot be answered with the available tools, say "I can only help with calculations, text length, and text reversal using my tools."
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
            
            # Stream through agent events using the latest stream_mode="updates" pattern
            # See: https://docs.langchain.com/oss/python/langchain/streaming
            async for chunk in agent.astream(
                {"messages": [{"role": "user", "content": user_input}]},
                stream_mode="updates"
            ):
                for step, data in chunk.items():
                    messages = data.get("messages", [])
                    if not messages:
                        continue
                    
                    last_message = messages[-1]
                    
                    # "model" step: LLM is generating a response (may include tool calls)
                    if step == "model":
                        # Check if the model is requesting tool calls
                        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                            for tool_call in last_message.tool_calls:
                                tool_call_count += 1
                                tool_name = tool_call.get("name", "unknown")
                                tool_args = tool_call.get("args", {})
                                
                                print(f"🔧 Tool Call #{tool_call_count}: {tool_name}")
                                
                                # Show what the agent is passing to the tool
                                for key, value in tool_args.items():
                                    print(f"   └─ {key}: {value}")
                        else:
                            # Final answer from the model (no tool calls)
                            # Use content_blocks for standardized access, fallback to content
                            content = (
                                last_message.content_blocks[0].get("text", "")
                                if hasattr(last_message, "content_blocks") and last_message.content_blocks
                                else last_message.content
                            )
                            if content:
                                print(f"💡 Agent's Reasoning & Answer:")
                                print(f"   {content}")
                                print(f"\n📊 Summary: Used {tool_call_count} tool call(s) across {step_number} step(s)")
                    
                    # "tools" step: Tool execution completed
                    elif step == "tools":
                        step_number += 1
                        # Use content_blocks for standardized access, fallback to content
                        tool_output = (
                            last_message.content_blocks[0].get("text", "")
                            if hasattr(last_message, "content_blocks") and last_message.content_blocks
                            else last_message.content
                        )
                        print(f"\n✅ Step {step_number} Complete: {last_message.name}")
                        print(f"   └─ Output: {tool_output}")
                        print()
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n⚠️  Set OPENROUTER_API_KEY before running!")
    print("Get your key at: https://openrouter.ai/keys\n")
    asyncio.run(streaming_multi_step_agent())