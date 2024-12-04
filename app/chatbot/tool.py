from app.services.search import SearchService
from app.schemas.study import CreateStudySchema as StudyType 
from app.schemas.search import PacienteSearch
from typing import TypedDict
from app.chatbot import llm 

def api_tool(search_data: TypedDict) -> list[StudyType]:
    search_service = SearchService()
    if search_data.get("location"):
        search_data = PacienteSearch(
            location = search_data["location"],
            condition = search_data["condition"],
            status = ["RECRUITING"],
        )
        result = search_service.search_paciente(search_data)
        return result

    search_data = PacienteSearch(
        condition = search_data["condition"],
        location = "Brazil",
        status = ["RECRUITING"],
    )

    result = search_service.search_paciente(search_data)

    return result
    
    