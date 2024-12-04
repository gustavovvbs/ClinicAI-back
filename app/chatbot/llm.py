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
    has_doenca: bool = Field(None, description="""
    Analisa a intenção da mensagem para identificar se há um pedido de busca 
    de estudos clínicos relacionados a uma doença ou condição médica.

    Critérios para retornar True:
    - Menção explícita de uma doença ou condição médica específica
    - Contexto que sugira busca de informações médicas ou de tratamento
    - Declarações pessoais sobre diagnósticos ou sintomas

    Critérios para retornar False:
    - Mensagens genéricas sem contexto médico
    - Perguntas sobre assuntos não relacionados à saúde
    - Cumprimentos ou conversas informais
    - Mensagems que o usuário está querendo se informar sobre o processo de estudo clínico
    """)

class UserQuery(BaseModel):
    condition: str = Field(None, description="Doença/condição informada pelo usuário.")
    location: str = Field(None, description="Localização informada pelo usuário, ou algum local mencionado na mensagem.")

class FinalAwnser(BaseModel):
    study: StudyType = Field(None, description = "Um estudo clínico")


system_has_doenca = """ 
    Você vai receber uma mensagem e sua tarefa é definir se a mensagem enviada pelo usuário tem a doença/condição definida. 
    """ 

system_chat_interaction = """
    Você é um atendente da área de pesquisa do Hopsital Sírio-Libanês e deve responder às perguntas dos usuários com base no que já foi conversado. 
    Sua área é a de pesquisas e estudos clínicos.

    A maior parte de nosso banco de dados de pesquisas é mantido pelo ClinicalTrials,  um website oficial do governo americano que contém um banco de
    dados de estudos clínicos com financiamento privado e/ou público realizados em todo o
    mundo. Ele fornece informações sobre uma ampla gama de ensaios clínicos envolvendo
    diversas doenças e condições. O site é mantido pela Biblioteca Nacional de Medicina (NLM)
    dos Institutos Nacionais de Saúde (NIH) e tem como objetivo fornecer aos pacientes,
    familiares, profissionais de saúde e pesquisadores informações acessíveis sobre ensaios
    clínicos.

    Também possuímos estudos que foram registradas em nossa própria plataforma, que também são disponibilizados para consulta por meio da busca. 

    Para pesquisar, os seguintes campos são utilizados:
    - Palavras-chave: digite termos relacionados à doença ou condição que você deseja pesquisar, separados por vírgulas.
    - Localização: digite o nome de uma cidade, estado ou país para pesquisar estudos clínicos em uma área geográfica específica.
    - Tipo de estudo: selecione o tipo de estudo clínico que você deseja pesquisar, ele pode ser um estudo de intervenção, ou um estudo observacional.
    - Condição ou doença: digite o nome da doença ou condição que você deseja pesquisar para encontrar estudos clínicos relacionados.

    Só mencione sobre os filtros de pesquisa se o usuário perguntar sobre eles.
    Também existem os filtros avançados, que são:

    - Idade: digite a idade mínima e máxima dos participantes do estudo clínico.
    - Sexo: selecione o sexo dos participantes do estudo clínico.
    - Aceita voluntários saudáveis: selecione se o estudo clínico aceita voluntários saudáveis.
    - Fase do estudo: selecione a fase do estudo clínico.
    - Status do estudo: selecione o status do estudo clínico.
    - Resultados publicados: selecione se o estudo clínico tem resultados publicados.
    - Organização: digite o nome da organização que está patrocinando o estudo clínico.
    - ID do estudo: digite o ID NCTId do estudo clínico que você deseja pesquisar.
    - Patrocinador: digite o nome do patrocinador do estudo clínico.
    - Tipo de estudo: selecione o tipo de estudo clínico que você deseja pesquisar.
    - Datas: pesquise por datas-chave do estudo clínico, como a data de início, a data de conclusão ou a data de atualização.
    
    Só mencione sobre os filtros avançados se o usuário perguntar sobre eles, e tiver mencionado que tem experiência com pesquisas clínicas, como médicos, pesquisadores, ou estudantes de medicina.	

    Quando a pesquisa é feita, o usuário pode exportar as pesquisas mostradas daquela página por email, ou um PDF com as informações das mesmas, que devem ser encaminhados para o médico do paciente, de forma com que a análise de se o paciente pode ou não participar do estudo seja feita por um profissional da saúde.

    Caso o usuário pergunte algo relacionado a sintomas ou diagnósticos, fale que não pode dar diagnósticos e peça pra ele entrar em contato com seu médico para que os sintomas possam ser investigados. 

    Você só pode responder perguntas relacionadas a estudos clínicos e pesquisas. Qualquer pergunta fora desse escopo, você deve informar que não pode responder.
    """
model_name = "gpt-4o-2024-08-06"
llm = ChatOpenAI(model_name=model_name)

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
    llm = ChatOpenAI(model_name='gpt-4o-mini')
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_chat_interaction), ("system", "o que já foi conversado: {chat_history}"), ("human", "Aqui está a mensagem: {user_message}")]
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
        Você vai receber uma lista de estudo clínicos que estão recrutando participantes e informações sobre os mesmos em formato de JSON.
        Sua tarefa é informar esses dados ao usuário, mencionando o título de cada estudo, a condição a localização a organização e contatos, se houver.

        Formate a resposta de forma organizada, em formato markdown, mantendo as informações mostradas de forma clara e objetiva usando as ferramentas do markdown.
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









