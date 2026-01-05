from fastapi import FastAPI
from app.db.get_all_tables import execute_sql
from app.langgraph.langgraph_nodes import compile_graph
from app.langgraph.SqlAnalyst_State import SqlAnalystState
app=FastAPI()

@app.get("/")
def test_api(quations:str):
    state = {
        "question":quations,
    }
    graph=compile_graph()
    response=graph.invoke(state)
    return response

@app.get("/query")
def run_query():
    row=execute_sql("select count(*) from users")
    return row
