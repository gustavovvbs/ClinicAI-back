import os 
from dotenv import load_dotenv
from pinecone import Pinecone
from app.models.study import StudyModel 
from app.schemas.study import CreateStudySchema
from flask import current_app
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from bson import ObjectId
from typing import Optional

load_dotenv()

class StudyService:
    def __init__(self):
        self.db = current_app.mongo
        pc = Pinecone()
        index_name = "sprint-hsl"
        self.embeddings_model = OpenAIEmbeddings()
        self.index = pc.Index(name = index_name)
        self.vector_store = PineconeVectorStore(index_name, embedding=self.embeddings_model)

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

        study_data = study.model_dump()
        created_study = self.db.studies.insert_one(study_data)
        inserted_id = str(created_study.inserted_id)

        #add study to pinecone
        self.vector_store.add_documents([study_data], ids=[inserted_id])

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

        self.index.update(
            id=study_id,
            set_metadata={"sub_status": "accepted"}
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

        self.index.update(
            id = study_id,
            set_metadata={"sub_status": "rejected"}
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




       