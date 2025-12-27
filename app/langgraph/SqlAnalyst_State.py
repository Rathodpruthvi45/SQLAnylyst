from typing import Annotated,TypedDict

from langgraph.graph.message import add_messages


class SqlAnalystState(TypedDict):
    quations:str
    schema:str
    table_name:str
    query:str
    error:str
    messages:Annotated[list,add_messages]
    retry_count:int

