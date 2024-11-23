from pydantic import BaseModel, Field 
from typing import Optional 
from app.models.location import LocationModel 
from app.models.contact import ContactModel
from app.models.intervention import InterventionModel

class StudyModel(BaseModel):
    Title: str = Field(None, description="Title of the study")
    Description: str = Field(None, description="Description of the study")
    Interventions: list[InterventionModel] = Field(None, description="Intervention of the study")
    InterventionNames: list[str]
    Sponsor: str = Field(None, description="Sponsor of the study")
    FunderType: str = Field(None, description="Funder type of the study")
    Organization: str = Field(None, description="Organization of the study")
    StartDate: str = Field(None, description="Start date of the study")
    EndDate: str = Field(None, description="End date of the study")
    Keywords: str = Field(None, description="Keywords of the study")
    Status: list[str] = Field(None, description="Status of the study")
    Location: list[LocationModel] = Field(None, description="Location of the study")
    Conditions: list[str] = Field(None, description="Condition of the study")
    MinimumAge: str = Field(None, description="Minimum age of the study")
    MaximumAge: str = Field(None, description="Maximum age of the study")
    Restrictions: str = Field(None, description="Restrictions of the study")
    Sex: str = Field(None, description="Biological sex of people that can participate in the study")
    StudyType: str = Field(None, description="Type of the study")
    Phase: str = Field(None, description="Phase of the study")
    HealthyVolunteers: bool = Field(True, description="Healthy volunteers of the study")
    endDate: str = Field(None, description="Estimated end date of the study")
    Contacts: list[ContactModel] = Field(None, description="Contacts of the study")
    isAccepted: Optional[bool] = Field(False, description="If the study is accepted")
