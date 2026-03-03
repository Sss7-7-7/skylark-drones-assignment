import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

MONDAY_URL = "https://api.monday.com/v2"

def get_headers():
    return {
        "Authorization": os.getenv("MONDAY_API_KEY"),
        "API-Version": "2023-10",
        "Content-Type": "application/json"
    }

def fetch_board_data(board_id: str) -> str:
    query = f"""
    query {{
      boards (ids: {board_id}) {{
        items_page (limit: 100) {{
          items {{
            name
            column_values {{
              id
              text
            }}
          }}
        }}
      }}
    }}
    """
    try:
        response = requests.post(MONDAY_URL, json={'query': query}, headers=get_headers())
        response.raise_for_status()
        data = response.json()
        
        items = data.get("data", {}).get("boards", [{}])[0].get("items_page", {}).get("items", [])
        if not items:
            return "No data found on this board."
        
        # Extract headers (keys) dynamically
        headers = ["Item Name"]
        for col in items[0].get("column_values", []):
            headers.append(col.get("id"))
            
        # Build a highly compact Pipe-Separated Values (PSV) string
        lines = ["|".join(headers)]
        for item in items:
            row_data = [str(item.get("name", "")).replace("|", "")]
            for col in item.get("column_values", []):
                val = str(col.get("text", "")).replace("|", "").replace("\n", " ")
                row_data.append(val)
            lines.append("|".join(row_data))
            
        compact_data = "\n".join(lines)
        
        # TOKEN LIMIT SAFEGUARD: 1 token is roughly 4 characters. 
        # Limit to 20,000 characters (~5,000 tokens) to stay safe within Sarvam's 7k limit.
        MAX_CHARS = 20000 
        if len(compact_data) > MAX_CHARS:
            compact_data = compact_data[:MAX_CHARS] + "\n...[DATA TRUNCATED DUE TO TOKEN LIMIT]"
            
        return compact_data
    
    except Exception as e:
        return f"Error fetching data: {str(e)}"

# Keep fetch_deals() and fetch_work_orders() exactly as they are.

def fetch_deals() -> str:
    """Tool to fetch live data from the Deals board."""
    board_id = os.getenv("DEALS_BOARD_ID")
    return fetch_board_data(board_id)

def fetch_work_orders() -> str:
    """Tool to fetch live data from the Work Orders board."""
    board_id = os.getenv("WORK_ORDERS_BOARD_ID")
    return fetch_board_data(board_id)