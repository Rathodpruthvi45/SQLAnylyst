from typing import Annotated,TypedDict,List

from langgraph.graph.message import add_messages


class SqlAnalystState(TypedDict, total=False):
    question: str
    table_name: str
    schema: List[str]
    sql_query: str
    error: str
    messages: Annotated[List[str], add_messages]
    retry_count: int
    is_safe:bool
    is_sql_valid:bool
    query_result:list[dict]

