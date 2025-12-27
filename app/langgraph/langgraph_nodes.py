
from langgraph.graph import StateGraph,START,END
from app.langgraph.SqlAnalyst_State import SqlAnalystState
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import json
from app.db.get_all_tables import get_all_tables_schema
os.environ["GOOGLE_API_KEY"] ="AIzaSyDG4deiAwG4_SLJGNKX9CWm08YIrm1Jaiw"

model=ChatGoogleGenerativeAI(model="gemini-2.5-flash")


def validate_question(state:SqlAnalystState):
    question=state['question']
    if not question:
        raise ValueError("No question is found")
    
    prompt=f"""
    You are a security validation service for a SQL system.

    Your task is to analyze the user question and determine
    whether it is SAFE or UNSAFE.

    Rules:
    - UNSAFE if the question involves:
    - DELETE data
    - DROP tables or databases
    - UPDATE records
    - INSERT new records
    - ALTER tables
    - TRUNCATE tables
    - SAFE only if the question is READ-ONLY (SELECT queries).

    Return ONLY valid JSON.
    DO NOT explain.
    DO NOT add markdown.
    DO NOT add text.

    JSON format:
    {{
    "is_safe": true | false,
    "reason": "short reason"
    }}

    User question:
    {question}
    """
    response = model.invoke(prompt)
    
    data=response.content

    try:
        data_with_json = json.loads(data)
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON")
    
    
    return {"is_safe":data_with_json['is_safe']}

def safety_router(state: SqlAnalystState):
    if state.get("is_safe"):
        return "choose_tables"
    else:
        return END
    

def choose_tables(state: SqlAnalystState):

    user_question=state["question"]

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
    data=response.content
    
    if not data or not data.strip():
        raise ValueError("LLM returned empty response")
    
    data=data.strip()

    if data.startswith("```"):
        data=data.replace("```json","").replace("```","").strip()
    try:
        data_with_json = json.loads(data)
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON")

    
    if "table" not in data_with_json or "columns" not in data_with_json:
        raise ValueError("LLM response missing required fields")

    return {
        "table_name": data_with_json["table"],
        "schema": data_with_json["columns"]
    }



#using the schemas creating the sql query and finding the ans 
def create_question(state:SqlAnalystState):
    question = state.get("question")
    table_name = state.get("table_name")
    schema = state.get("schema")
    print(question)
    if not question:
        raise ValueError("Missing required state for SQL generation")
    print(table_name)
    if table_name is None:
        raise ValueError("Table name is missing")

    if schema is None:
        raise ValueError("Table schema is missing")
    

    prompt=f"""
    You are a senior SQL engineer.

    Generate ONLY a valid SQL query.
    DO NOT explain.
    DO NOT add markdown.
    DO NOT add comments.
    DO NOT add text.

    Rules:
    - Use table: {table_name}
    - Allowed columns: {schema}
    - Do not invent columns
    - If aggregation is needed, use SQL functions
    - Use standard SQL syntax

    User question:
    {question}

    Return only SQL.
    """
    response = model.invoke(prompt)
    print(response.content)
    sql_query=response.content
    return {"sql_query":sql_query}





def compile_graph():
    graph=StateGraph(SqlAnalystState)
    graph.add_node(validate_question,"validate_question")
    graph.add_node(choose_tables,"choose_tables")
    graph.add_node(create_question,"create_question")
    graph.set_entry_point("validate_question")
    graph.add_conditional_edges("validate_question",safety_router, {
        "choose_tables": "choose_tables",
        END: END,
    })

    graph.add_edge("choose_tables","create_question")
    graph.add_edge("create_question",END)

    app = graph.compile()
    return app

    

    

