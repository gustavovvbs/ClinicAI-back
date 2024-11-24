from pydantic import BaseModel, Field 

class ResearcherModel(BaseModel):
    name: str = Field(None, description="Name of the researcher")
    affiliation: str = Field(None, description="Affiliation of the researcher")
    role: str = Field(None, description="Role of the researcher")