from pydantic import BaseModel, Field

class LocationModel(BaseModel):
    City: str = Field(None, description="City of the study")
    Country: str = Field(None, description="Country of the study")
    State: str = Field(None, description="State of the study")
    Facility: str = Field(None, description="Facility of the study")
    Status: str = Field(None, description="Status of the study")