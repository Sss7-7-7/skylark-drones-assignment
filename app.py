import streamlit as st
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from monday_api import fetch_deals, fetch_work_orders

# Load environment variables
load_dotenv()

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the tools available to the LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "fetch_deals",
            "description": "Fetches live data from the Deals funnel board. Use this for pipeline, deal value, probability, and deal stages queries.",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_work_orders",
            "description": "Fetches live data from the Work Order tracker board. Use this for queries about project execution, billing, and collected amounts.",
        }
    }
]

# System Prompt ensuring Data Resilience & formatting constraints
SYSTEM_PROMPT = """You are an elite Business Intelligence Agent for a busy founder. 
Your job is to answer queries using live data from Monday.com. 
CRITICAL INSTRUCTIONS:
1. ALWAYS trigger your tools to fetch live data. DO NOT guess.
2. The data is messy. You must handle nulls, missing values, and inconsistent formatting in your reasoning.
3. ALWAYS state data quality caveats (e.g., "Note: 4 deals were missing sector information").
4. Provide precise, executive-level summaries and actionable insights.
5. If a query is ambiguous, ask a clarifying question.
"""

st.title("📊 Founder BI Agent (Live Monday.com)")
st.caption("Ask questions about your Deals pipeline and Work Orders. Traces will appear when live data is fetched.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Display chat history (skipping the hidden system prompt)
for msg in st.session_state.messages:
    if msg["role"] != "system" and msg["role"] != "tool":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("E.g., How's our pipeline looking for the mining sector?"):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process via LLM
    with st.chat_message("assistant"):
        # We use st.status to create the visible Action/Tool-Call trace required by the assignment
        with st.status("Thinking...", expanded=True) as status:
            
            # Step 1: Send user prompt to LLM to see if it wants to use a tool
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages,
                tools=tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            st.session_state.messages.append(response_message)
            
            # Step 2: Check if LLM decided to call a tool
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    status.update(label=f"Triggering Live API Call: `{function_name}`...", state="running")
                    
                    # Execute the correct function
                    if function_name == "fetch_deals":
                        function_response = fetch_deals()
                    elif function_name == "fetch_work_orders":
                        function_response = fetch_work_orders()
                    else:
                        function_response = "Error: Tool not found."
                        
                    status.write(f"✅ Data retrieved from Monday.com via {function_name}")
                    
                    # Append the raw data back to the conversation context
                    st.session_state.messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )
                
                status.update(label="Analyzing messy data and generating insights...", state="running")
                
                # Step 3: Get final response from LLM using the newly fetched live data
                final_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=st.session_state.messages
                )
                
                final_answer = final_response.choices[0].message.content
                status.update(label="Complete!", state="complete")
                
            else:
                # If no tools were called (e.g., standard conversation)
                final_answer = response_message.content
                status.update(label="Complete!", state="complete")
        
        # Display the final synthesized answer
        st.markdown(final_answer)
        st.session_state.messages.append({"role": "assistant", "content": final_answer})