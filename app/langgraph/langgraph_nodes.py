
from langgraph.graph import StateGraph,START,END
from app.langgraph.SqlAnalyst_State import SqlAnalystState
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import json
from app.db.get_all_tables import get_all_tables_schema,execute_sql
from app.core.config import settings
from dotenv import load_dotenv
load_dotenv()

FORBIDDEN = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
model=ChatGoogleGenerativeAI(model="gemini-2.5-flash",google_api_key=settings.GOOGLE_API_KEY)


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
    sql_query=""
    try:

        response = model.invoke(prompt)

        sql_query=response.content
    except Exception as e:
        print(e)
    return {"sql_query":sql_query}

def check_query_is_correct_as_per_quations(state:SqlAnalystState):
    table_name=state['table_name']
    schema=state['schema']
    question=state['question']
    sql_query=state['sql_query']

    if not sql_query:
        return {
            "is_sql_valid": False,
            "error": "SQL query missing"
        }

    if not sql_query.strip().upper().startswith("SELECT"):
        return {
            "is_sql_valid": False,
            "error": "Only SELECT queries are allowed"
        }

    if any(word in sql_query.upper() for word in FORBIDDEN):
        return {
            "is_sql_valid": False,
            "error": "Dangerous SQL detected"
        }
    prompt=f"""
    You are a SQL security and correctness validator.

    Your task is to verify whether the given SQL query is:
    1. SAFE (read-only)
    2. CORRECT for the user question
    3. VALID according to the table schema

    Rules:
    - ONLY SELECT queries are allowed
    - DO NOT allow:
    DELETE, DROP, UPDATE, INSERT, ALTER, TRUNCATE
    - Query must use table: {table_name}
    - Query must ONLY use columns from this list:
    {schema}
    - Do NOT invent tables or columns
    - SQL must logically answer the user question

    Return ONLY valid JSON.
    DO NOT explain.
    DO NOT add markdown.
    DO NOT add extra text.

    JSON format:
    {{
    "is_sql_valid": true | false,
    "reason": "short reason if invalid"
    }}

    User question:
    {question}

    SQL query:
    {sql_query}
    """
    response = model.invoke(prompt)
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "is_sql_valid": False,
            "error": "Invalid JSON from SQL verification model"
        }
    return {
        "is_sql_valid": True
    }

def sql_verification_router(state: SqlAnalystState):
    if state.get("is_sql_valid"):
        return "execute_sql_node"
    else:
        return END

def execute_sql_node(state: SqlAnalystState):

    sql=state['sql_query']
    results=execute_sql(sql)
    return {
        "query_result":results
    }

# def compile_graph():
#     graph=StateGraph(SqlAnalystState)
#     graph.add_node(validate_question,"validate_question")
    
#     graph.add_node(choose_tables,"choose_tables")
#     graph.add_node(create_question,"create_question")
#     graph.set_entry_point("validate_question")
#     graph.add_conditional_edges("validate_question",safety_router, {
#         "choose_tables": "choose_tables",
#         END: END,
#     })

#     graph.add_edge("choose_tables","create_question")
#     graph.add_edge("create_question",END)

#     app = graph.compile()
#     return app

    

    



def compile_graph():
    graph = StateGraph(SqlAnalystState)

    # Nodes
    graph.add_node("validate_question", validate_question)
    graph.add_node("choose_tables", choose_tables)
    graph.add_node("create_question", create_question)
    graph.add_node("check_sql", check_query_is_correct_as_per_quations)
    graph.add_node("execute_sql_node", execute_sql_node)

    # Entry point
    graph.set_entry_point("validate_question")

    # Question safety routing
    graph.add_conditional_edges(
        "validate_question",
        safety_router,
        {
            "choose_tables": "choose_tables",
            END: END,
        }
    )

    # Main flow
    graph.add_edge("choose_tables", "create_question")
    graph.add_edge("create_question", "check_sql")

    # SQL safety routing
    graph.add_conditional_edges(
        "check_sql",
        sql_verification_router,
        {
            "execute_sql_node": "execute_sql_node",
            END: END,
        }
    )

    # End
    graph.add_edge("execute_sql_node", END)

    return graph.compile()
