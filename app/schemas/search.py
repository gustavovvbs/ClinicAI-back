from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional , List


class PacienteSearch(BaseModel):
    keywords: Optional[str] = Field(None, alias="query.term")
    condition: Optional[str] = Field(None, alias="query.cond")
    status: Optional[List[str]] = Field(None, alias="filter.overallStatus")
    location: Optional[str] = Field(None, alias="query.locn")
    intervention: Optional[str] = Field(None, alias="query.intr")
    sponsor: Optional[str] = Field(None, alias="query.lead")
    age: Optional[str] = Field(None, alias="filter.advanced")
    sex: Optional[str] = Field(None, alias="eligibilityModule.sex")

    pageToken: Optional[str] = None
    page: Optional[str] = Field(None, alias="page")

    @model_validator(mode="before")
    def convert_empty_to_none(cls, values):
        """Convert empty strings, empty lists, and whitespace-only strings to None"""
        if not isinstance(values, dict):
            return values
            
        def is_empty(v):
            if isinstance(v, str):
                return not v.strip()
            if isinstance(v, (list, dict)):
                return len(v) == 0
            return False

        return {
            k: None if is_empty(v) else v 
            for k, v in values.items()
        }

    model_config = ConfigDict(populate_by_name=True)

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
    page: Optional[str] = Field(None, alias="page")

    @model_validator(mode="before")
    def convert_empty_to_none(cls, values):
        """Convert empty strings, empty lists, and whitespace-only strings to None"""
        if not isinstance(values, dict):
            return values
            
        def is_empty(v):
            if isinstance(v, str):
                return not v.strip()
            if isinstance(v, (list, dict)):
                return len(v) == 0
            return False

        return {
            k: None if is_empty(v) else v 
            for k, v in values.items()
        }
        
    model_config = ConfigDict(populate_by_name=True)

