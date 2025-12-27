

from app.langgraph.SqlAnalyst_State import SqlAnalystState
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import json
from app.db.get_all_tables import get_all_tables_schema
os.environ["GOOGLE_API_KEY"] ="AIzaSyAkLEmiJg9IXk-LAoKOojQkYDhxTG2py9U"

model=ChatGoogleGenerativeAI(model="gemini-2.5-flash")




def choose_tables(state: SqlAnalystState):
    user_question = state.get("quations", "").strip()

  
    if not user_question:
        return {}

    all_tables_schemas = get_all_tables_schema()

    prompt = f"""
You are a database schema selector.

Your task:
Select EXACTLY ONE database table that is MOST relevant to the user's question.

IMPORTANT RULES (STRICT):
- Select ONLY ONE table
- Use ONLY the provided schema
- Do NOT invent tables or columns
- Include ONLY relevant columns
- Output VALID JSON ONLY
- No explanation

User Question:
{user_question}

Database Schema (JSON):
{all_tables_schemas}

Output Format (STRICT JSON ONLY):
{{
  "table": "table_name",
  "columns": [
    {{
      "column": "column_name",
      "type": "DATA_TYPE",
      "primary_key": true,
      "not_null": true,
      "default": null
    }}
  ]
}}
"""

    response = model.invoke(prompt)

    try:
        data = json.loads(response.content)
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON")

    
    if "table" not in data or "columns" not in data:
        raise ValueError("LLM response missing required fields")

    return {
        "table_name": data["table"],
        "schema": data["columns"]
    }



#using the schemas creating the sql query and finding the ans 
def create_quations(state:SqlAnalystState):
    table_name=state.get("table", "").strip()
    table_schemas=state.get("schema", "").strip()

    if table_name is None:
        raise ValueError("Table name is missing")

    if table_schemas is None:
        raise ValueError("Table schema is missing")

    

    

