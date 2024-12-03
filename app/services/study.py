from app.models.study import StudyModel 
from app.schemas.study import CreateStudySchema
from flask import current_app
from bson import ObjectId
from typing import Optional

class StudyService:
    def __init__(self):
        self.db = current_app.mongo

    def create_study(self, study: CreateStudySchema, status: Optional[str] = None) -> str:
        """
        Creates a study in the database. 

        Args:
            study (CreateStudySchema): Study to be created

        Returns:
            str: Message with the id of the created study
        """
        #convert from api schema to intern mdoel 
        study = StudyModel(
            **study.model_dump(),
            isAccepted=False
        )
        created_study = self.db.studies.insert_one(study.model_dump())
        return f"Study created successfully with id {created_study.inserted_id}"

    def approve_study(self, study_id: str):
        """ 
        Approves a study to be shown in the platform by its id 

        Args:
            study_id (str): Study id to be approved

        Returns:
            str: Message with the result of the operation
        """
        study = self.db.studies.find_one({"_id": ObjectId(study_id)})
        if not study:
            return ValueError("Study not found")
        if study.get("sub_status") == "accepted":
            raise ValueError("Study already approved")

        self.db.studies.update_one(
            {"_id": ObjectId(study_id)},
            {"$set": {"sub_status": "accepted"}}
        )
       
        return "Study successfully accepted"
        
    def reject_study(self, study_id: str) -> str:
        """
        Rejects a study to be shown in the platform by its id 

        Args:
            study_id (str): Study id to be rejected

        Returns:
            str: Message with the result of the operation
        """
        study = self.db.studies.find_one({"_id": ObjectId(study_id)})
        if not study:
            return ValueError("Study not found")
        if study.get("sub_status") == "rejected":
            raise ValueError("Study already rejected")

        self.db.studies.update_one(
            {"_id": ObjectId(study_id)},
            {"$set": {"sub_status": "rejected"}}
        )

        return "Study successfully rejected"

    def get_studies(self):
        studies = list(self.db.studies.find())
        for study in studies:
            study["_id"] = str(study["_id"])
        return studies

    def get_study(self, study_id: str):
        study = self.db.studies.find_one({"_id": ObjectId(study_id)})
        if not study:
            return "Study not found"
        study["_id"] = str(study["_id"])
        return study




       