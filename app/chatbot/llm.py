from operator import itemgetter 
from typing import TypedDict 

from app.schemas.study import CreateStudySchema as StudyType
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_openai import ChatOpenAI

def prompt_has_doenca(message: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [("system", message), ("human", "Aqui está a mensagem: {user_message}")]
    )

def extract_query_dict(response) -> dict:
    query_dict = {}
    for tool_call in response.tool_calls:
        if tool_call["name"] == "UserQuery":
            query_dict.update(tool_call["args"])
    return query_dict

def prompt_extract_data(message: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [("system", "Você vai receber uma mensagem de um usuário e deve extrair dessa mensagem a condição/doença que ele informou."), ("human", "Aqui está a mensagem: {user_message}")]
    )

class HasDoenca(BaseModel):
    has_doenca: bool = Field(None, description="Se a mensagem que o usuário enviou tem a doença/condição definida.")

class UserQuery(BaseModel):
    condition: str = Field(None, description="Doença/condição informada pelo usuário.")
    location: str = Field(None, description="Localização informada pelo usuário, ou algum local mencionado na mensagem.")

class FinalAwnser(BaseModel):
    study: StudyType = Field(None, description = "Um estudo clínico")


system_has_doenca = """ 
    Você vai receber uma mensagem e sua tarefa é definir se a mensagem enviada pelo usuário tem a doença/condição definida. 
    """ 

# model_name = "gpt-4o-mini"
# llm = ChatOpenAI(model_name=model_name)

def has_doenca_classify(message: str) -> bool:
    llm_extractor = llm.bind_tools([HasDoenca])
    prompt = prompt_has_doenca(message)
    chain_classifier = (
        {"user_message": itemgetter("user_message")}
        | prompt 
        | llm_extractor
    )

    response = chain_classifier.invoke({"user_message": message})
    return response.tool_calls[0]['args']['has_doenca']

def awnser_chat_interaction(message: str, chat_history: list[str]) ->str:
    prompt = ChatPromptTemplate.from_messages(
        [("system", "Você é um atendente da área de pesquisa do Hopsital Sírio-Libanês e deve responder às perguntas dos usuários com base no que já foi conversado"), ("system", "o que já foi conversado: {chat_history}"), ("human", "Aqui está a mensagem: {user_message}")]
    )

    chain = (
        {"user_message": itemgetter("user_message"), "chat_history": itemgetter("chat_history")}
        | prompt
        | llm
        | StrOutputParser()
    )

    response = chain.invoke({"user_message": message, "chat_history": chat_history})
    return response

def schema_message(message: str) -> TypedDict:
    llm_extractor = llm.bind_tools([UserQuery])
    prompt = prompt_extract_data(system_has_doenca)
    chain_extractor = (
        {"user_message": itemgetter("user_message")}
        | prompt
        | llm_extractor
    )
    response = chain_extractor.invoke({"user_message": message})
    response = extract_query_dict(response)
    return response

def awnser_with_results(results: list[StudyType]) -> str:
    awnser_prompt = """ 
        Você vai receber uma lista de estudo clínicos e informações sobre os mesmos em formato de JSON.
        Sua tarefa é informar esses dados ao usuário, mencionando o título de cada estudo, a condição a localização a organização e contatos, se houver.
        """ 
    
    awnser_prompt = ChatPromptTemplate.from_messages(
        [("system", awnser_prompt), ("human", "Aqui estão os dados: {results}")]
    )

    dados = str(results)

    chain_awnser = (
        {"results": itemgetter("dados")}
        | awnser_prompt
        | llm
        | StrOutputParser()
    )

    response = chain_awnser.invoke({"dados": dados})
    return response









