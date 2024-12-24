"""
Multi round dialogue with langgraph, support automatic memory and multiprocess conversation
Reference: https://python.langchain.com/docs/tutorials/chatbot/
Dependencies:
```
pip install langchain-core, langgraph>0.2.27
pip install -qU langchain-mistralai
```
"""
import os
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, AIMessage
# langgraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "XXX" # TODO
os.environ["MISTRAL_API_KEY"] = "XXX" # TODO


model = ChatMistralAI(model="mistral-large-latest")

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)


# Define the function that calls the model
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}


# Define the (single) node in the graph
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Use thread_id to identify which conversation is we on
thread_id = "1"

while True:
    thread_id_new = input(f"Enter thread_id (Default to {thread_id}): ")
    if thread_id_new and thread_id_new != thread_id:
        thread_id = thread_id_new
        print(f' ================= Change to thread {thread_id_new} ================= \n')

    prompt = input("Human: ")
    if prompt == 'q': 
        break

    config = {"configurable": {"thread_id": thread_id}}
    input_messages = [HumanMessage(prompt)]
    output = app.invoke({"messages": input_messages}, config)
    print(f"AI({thread_id}):" + output["messages"][-1].content)  # output contains all messages in state
