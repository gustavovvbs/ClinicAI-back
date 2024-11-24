from pydantic import BaseModel, Field 

class DateModel(BaseModel):
    date: str 
    type: str