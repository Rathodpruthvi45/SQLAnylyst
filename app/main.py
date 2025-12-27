from fastapi import FastAPI
from app.langgraph.langgraph_nodes import compile_graph
from app.langgraph.SqlAnalyst_State import SqlAnalystState
app=FastAPI()

@app.get("/")
def test_api():
    state = {
        "question": "Show total users",
    }
    graph=compile_graph()
    response=graph.invoke(state)
    return response

