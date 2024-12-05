from app.chatbot.graph_state import GraphState, Message
from app.chatbot import llm, tool 
from langchain_core.runnables import RunnableLambda

def workflow(state: GraphState) -> GraphState:
    if state.user_message:
        state.chat_history.append(Message(text=state.user_message, sender="user"))
        has_doenca = llm.has_doenca_classify(state.user_message)
        state.has_doenca = has_doenca
        if state.has_doenca:
            condition = llm.schema_message(state.user_message)
            state.studies_list = tool.api_tool(condition)
            response = llm.awnser_with_results(state.studies_list)
            state.chat_history.append(Message(text=response, sender="ai"))
        else:
            response = llm.awnser_chat_interaction(state.user_message, state.chat_history)
            state.chat_history.append(Message(text=response, sender="ai"))
    return state

compiled_workflow = RunnableLambda(lambda state: workflow(state))
            