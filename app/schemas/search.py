from pydantic import BaseModel, Field
from typing import Optional , List


class PacienteSearch(BaseModel):
    keywords: Optional[str] = Field(None, alias="query.term")
    condition: Optional[str] = Field(None, alias="query.cond")
    status: Optional[List[str]] = Field(None, alias="filter.overallStatus")
    location: Optional[str] = Field(None, alias="query.locn")
    intervention: Optional[str] = Field(None, alias="query.intr")
    sponsor: Optional[str] = Field(None, alias="query.lead")
    age: Optional[str] = None  
    sex: Optional[str] = Field(None, alias="eligibilityModule.sex")
    pageToken: Optional[str] = None

    class Config:
        populate_by_name = True

class MedicoSearch(BaseModel):
    title: Optional[str] = Field(None, alias="query.titles")
    keywords: Optional[str] = Field(None, alias="query.term")
    condition: Optional[str] = Field(None, alias="query.cond")
    status: Optional[List[str]] = Field(None, alias="filter.overallStatus")
    location: Optional[str] = Field(None, alias="query.locn")
    intervention: Optional[str] = Field(None, alias="query.intr")
    sponsor: Optional[str] = Field(None, alias="query.lead")
    age: Optional[str] = Field(None, alias="filter.advanced")
    sex: Optional[str] = Field(None, alias="query.aggFilters")
    acceptsHealthyVolunteers: Optional[bool] = Field(None, alias="query.aggFilters")
    studyPhase: Optional[str] = Field(None, alias="query.phase")
    studyType: Optional[str] = Field(None, alias="query.type")
    hasResults: Optional[bool] = Field(None, alias="query.aggFilters")
    organization: Optional[str] = Field(None, alias="query.advanced")
    studyId: Optional[str] = Field(None, alias="query.id")

    pageToken: Optional[str] = None

    class Config:
        populate_by_name = True

