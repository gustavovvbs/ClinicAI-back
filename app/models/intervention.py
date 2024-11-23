from pydantic import BaseModel, Field 

class InterventionModel(BaseModel):
    description: str = Field(None, description="Description of the intervention")
    interventionType: str = Field(None, description="Type of the intervention")
    explanation: str = Field(None, description="Explanation of the intervention")
    label: str = Field(None, description="Label of the intervention")
