from app.services.search import SearchService
from app.schemas.study import CreateStudySchema as StudyType 
from app.schemas.search import PacienteSearch
from typing import TypedDict
from app.chatbot import llm 

def api_tool(search_data: TypedDict) -> list[StudyType]:
    print(search_data)
    search_service = SearchService()
    search_data = PacienteSearch(
        location = search_data["location"],
        condition = search_data["condition"],
        status = ["RECRUITING"],
    )

    result = search_service.search_paciente(search_data)

    return result
    
    