from pydantic import BaseModel, Field 
from app.models.contact import ContactModel
from app.models.intervention import InterventionModel
from app.models.location import LocationModel
from app.models.researcher import ResearcherModel
from app.models.date import DateModel

class CreateStudySchema(BaseModel):
    Title: str = Field(None, description="Title of the study")
    Description: str = Field(None, description="Description of the study")
    Interventions: list[InterventionModel] = Field(None, description="Intervention of the study")
    InterventionNames: list[str]
    Sponsor: str = Field(None, description="Sponsor of the study")
    FunderType: str = Field(None, description="Funder type of the study")
    Organization: str = Field(None, description="Organization of the study")
    StartDate: DateModel = Field(None, description="Start date of the study")
    endDate: DateModel = Field(None, description="End date of the study")
    Keywords: list[str] = Field(None, description="Keywords of the study")
    Status: list[str] = Field(None, description="Status of the study")
    Location: list[LocationModel] = Field(None, description="Location of the study")
    Conditions: list[str] = Field(None, description="Condition of the study")
    MinimumAge: str = Field(None, description="Minimum age of the study")
    MaximumAge: str = Field(None, description="Maximum age of the study")
    Restrictions: str = Field(None, description="Restrictions of the study")
    Researchers: list[ResearcherModel] = Field(None, description="Researchers of the study")
    Contacts: list[ContactModel] = Field(None, description="Contacts of the study")
    PrimaryCompletionDate: DateModel = Field(None, description="Primary completion date of the study")  
    LastUpdatedPostDate: DateModel = Field(None, description="Last updated date of the study")
    Phase: list[str] = Field(None, description="Phase of the study")
    Sex: str = Field(None, description="Biological sex that can participate the study")
    StudyType: str = Field(None, description="Type of the study")
    HealhyVolunteers: bool = Field(True, description="Healthy volunteers of the study")
    HasPublishedResults: bool = Field(True, description="If the study has published results")
    
    

