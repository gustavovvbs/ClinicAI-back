from pymongo import MongoClient, IndexModel
from flask import current_app
from app.core.config import Config

def init_db(app):
    client = MongoClient(Config.MONGO_URI)
    db = client['sprint-hsl']
    db.local_studies.create_indexes([
        IndexModel("protocolSection.contactsLocationsModule.locations.country"),
        IndexModel("protocolSection.contactsLocationsModule.locations.facility"),
        IndexModel("protocolSection.designModule.studyType"),
        IndexModel("protocolSection.conditionsModule.conditions"),
        IndexModel("protocolSection.armsInterventionsModule.interventions.name"),
        IndexModel("protocolSection.designModule.phases")
    ])
    app.mongo = db
