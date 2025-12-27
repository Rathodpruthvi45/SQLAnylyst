from fastapi import FastAPI
from app.langgraph.langgraph_nodes import choose_tables
from app.langgraph.SqlAnalyst_State import SqlAnalystState
app=FastAPI()

@app.get("/")
def test_api():
    return choose_tables(SqlAnalystState)

