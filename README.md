
📊 Founder BI Agent (Live Monday.com)
A Streamlit-based Business Intelligence agent powered by OpenAI (gpt-4o) that acts as an elite data assistant for founders. The agent connects directly to Monday.com boards in real-time to answer complex, natural-language queries regarding Deals (pipelines, probabilities) and Work Orders (execution, billing).

Integration & Implementation Details
How did you integrate with Monday.com?
Integration with Monday.com is handled via its GraphQL API (API-Version: 2023-10) using the standard Python requests library.

A dynamic GraphQL query is constructed to fetch items_page (up to 100 items per request) from specific board_ids.

The JSON response is parsed to extract the item name and its corresponding column values.

To optimize for the LLM's context window and reduce token consumption, the parsed data is heavily compressed into a Pipe-Separated Values (PSV) format before being passed back to the LLM.

Did you implement live query-time fetching (no preloading/caching)?
Yes.

Data Fetching Strategy
There is absolutely no preloading, local database, or caching layer. The data fetching strategy is strictly query-time and reactive:

The user inputs a prompt.

The LLM evaluates the prompt and determines if it needs to trigger a function call (fetch_deals or fetch_work_orders).

If triggered, the Python backend makes a live HTTP POST request to Monday.com to pull the absolute latest state of the board.

The data is converted to a compact PSV string, truncated safely at 20,000 characters to prevent token limit errors, and injected directly into the LLM's context window.

The LLM processes the messy, live data and returns an actionable executive summary.

Brief Architecture Overview
The application follows a standard LLM Function Calling architecture:

Frontend (UI): Streamlit manages the chat interface, session state, and visual execution traces.

Brain (LLM): OpenAI API (gpt-4o) orchestrates the reasoning, decides when to trigger tools based on user intent, and synthesizes the final answer.

Tooling Layer: Python functions (fetch_deals, fetch_work_orders in monday_api.py) act as the bridge between the LLM and the external data source.

Data Source: Monday.com GraphQL API serves as the live system of record.

How does your agent display tool/API call traces?
The application uses Streamlit's native st.status container to create a highly visible, collapsible UI trace. When the LLM decides to trigger a tool, the UI dynamically updates its state:

🔄 "Thinking..." (LLM processing intent)

🏃 "Triggering Live API Call: fetch_deals..." (Executing the Python function)

✅ "Data retrieved from Monday.com via fetch_deals" (Successful API return)

🏃 "Analyzing messy data and generating insights..." (LLM parsing the raw PSV data)

🎉 "Complete!" (Final output rendered)

Setup Requirements
To run this application, ensure you have a .env file in your root directory containing:

OPENAI_API_KEY: Your OpenAI API Key.

MONDAY_API_KEY: Your Monday.com developer API key.

DEALS_BOARD_ID: The numeric ID of your Monday.com Deals board.

WORK_ORDERS_BOARD_ID: The numeric ID of your Monday.com Work Orders board.
