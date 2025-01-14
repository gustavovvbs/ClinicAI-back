from pydantic import BaseModel, Field
from typing import Optional, List 
from app.schemas.study import CreateStudySchema as StudyType

class Message(BaseModel):
    text: str
    sender: str 

class GraphState(BaseModel):
    user_message: Optional[str] = Field(None, description="User message")
    has_doenca: Optional[bool] = Field(None, description="if the state of the chat has doenca defined")
    studies_list: Optional[dict] = Field(None, description="List of studies fetched from the API")
    chat_history: Optional[List[Message]] = Field([], description="Chat history")


