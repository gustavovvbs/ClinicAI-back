from app.models.study import StudyModel 
from app.schemas.study import CreateStudySchema
from app.db.mongo_client import get_db
from bson import ObjectId

class StudyService:
    def __init__(self):
        self.db = get_db()

    def create_study(self, study: CreateStudySchema):
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
            return "Study not found"
        if study.get("isAccepted"):
            return "Study already accepted"
        self.db.studies.update_one({"_id": ObjectId(study_id)}, {"$set": {"isAccepted": True}})
        return "Study successfully accepted"


       