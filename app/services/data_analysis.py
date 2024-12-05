import requests
import atexit
from datetime import datetime
from pymongo import UpdateOne, DESCENDING
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.search import SearchService
from app.schemas.search import PacienteSearch


class DataService:
    def __init__(self, search_service: SearchService, db):
        self.BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
        self.search_service = search_service
        self.db = db
        self.collection = self.db["local_studies"]
    

    def _get_data_timestamp(self):
        response = requests.get('https://clinicaltrials.gov/api/v2/version')
        response.raise_for_status()
        data = response.json()

        return data.get("dataTimestamp")

    def _get_total_study_count(self):
        params = {
            "format": "json",
            "pageSize": 1,
            "countTotal": "true",
        }

        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        return data.get("totalCount", 0)

    def fetch_and_store_studies(self):
        last_update = self.db["metadata"].find_one({"_id": "data_timestamp"})
        if last_update:
            last_updated = last_update.get("last_updated")
            time_diff = datetime.utcnow() - last_updated
            if time_diff.days < 8:
                return  

        data_timestamp = self._get_data_timestamp()
        self.db["metadata"].update_one(
            {"_id": "data_timestamp"},
            {"$set": {"timestamp": data_timestamp, "last_updated": datetime.utcnow()}},
            upsert=True
        )

        page_token = None 
        page_size = 1000 

        total_global_studies = self._get_total_study_count()
        self.db["metadata"].update_one(
            {"_id": "total_global_studies"},
            {"$set": {"count": total_global_studies, "last_updated": datetime.utcnow()}},
            upsert=True
        )

        while True:
            params = {
                "query.locn": "Brazil",
                "pageSize": page_size,
                "format": "json",
            }        
            if page_token:
                params["pageToken"] = page_token

            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            studies_on_page = data.get("studies", [])

            operations = []
            for study in studies_on_page:
                nct_id = study.get("protocolSection", {}).get("identificationModule", {}).get("nctId")
                if nct_id:
                    study["last_updated"] = datetime.now()
                    operations.append(
                        UpdateOne(
                            {"protocolSection.identificationModule.nctId": nct_id},
                            {"$set": study},
                            upsert=True
                        )
                    )

            if operations:
                self.collection.bulk_write(operations)

            page_token = data.get("nextPageToken")
            if not page_token:
                break

    def get_representatividade(self):
        total_brazil_studies = self.collection.count_documents({})

        metadata =self.db["metadata"].find_one({"_id": "total_global_studies"})
        total_global_studies = metadata.get("count", 0) if metadata else 0

        if total_global_studies and total_brazil_studies > 0:
            representatividade = (total_brazil_studies / total_global_studies) * 100
        else:
            return {"representatividade": 0, "total_brazil_studies": 0, "total_global_studies": 0}

        response_dict = {
            "representatividade": representatividade,
            "total_brazil_studies": total_brazil_studies,
            "total_global_studies": total_global_studies,
        }

        return response_dict

    def get_top_centers(self):
        pipeline = [
            {"$unwind": "$protocolSection.contactsLocationsModule.locations"},
            {"$match": {"protocolSection.contactsLocationsModule.locations.country": "Brazil"}},
            {"$group": {
                "_id": "$protocolSection.contactsLocationsModule.locations.facility",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10},
        ]
        
        results = list(self.collection.aggregate(pipeline))

        top_centers = [{"facility": r["_id"], "count": r["count"]} for r in results if r["_id"]]

        response_dict = {"top_centers": top_centers}

        return response_dict

    def get_types_per_centers(self):
        pipeline = [
            {'$unwind': '$protocolSection.contactsLocationsModule.locations'},
            {'$match': {'protocolSection.contactsLocationsModule.locations.country': 'Brazil'}},
            {'$group': {
            '_id': {
                'facility': '$protocolSection.contactsLocationsModule.locations.facility',
                'studyType': '$protocolSection.designModule.studyType'
            },
            'count': {'$sum': 1}
            }},
            {'$group': {
            '_id': '$_id.facility',
            'types': {
                '$push': {
                'study_type': '$_id.studyType',
                'count': '$count'
                }
            },
            'totalCount': {'$sum': '$count'}
            }},
            {'$sort': {'totalCount': -1}},
            {'$limit': 10}
        ]

        results = list(self.collection.aggregate(pipeline))

        types_of_studies_per_center = {}
        for r in results:
            facility = r["_id"]
            types = r["types"]
            if facility:
                types_of_studies_per_center[facility] = types

        response_dict = {"types_of_studies_per_center": types_of_studies_per_center}

        return response_dict

    def get_main_diseases(self):
        pipeline = [
            {"$unwind": "$protocolSection.conditionsModule.conditions"},
            {"$group": {
                "_id": "$protocolSection.conditionsModule.conditions",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        results = list(self.collection.aggregate(pipeline))

        main_diseases = [{"disease": r["_id"], "count": r["count"]} for r in results]
        response_dict = {"main_diseases": main_diseases}
        return response_dict 

    def get_main_treatments(self):
        pipeline = [
            {'$unwind': '$protocolSection.armsInterventionsModule.interventions'},
            {'$group': {
                '_id': '$protocolSection.armsInterventionsModule.interventions.name',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        results = list(self.collection.aggregate(pipeline))

        main_treatments = [{"treatment": r["_id"], "count": r["count"]} for r in results]
        response_dict = {"main_treatments": main_treatments}
        return response_dict

    def get_phase_percentages(self):
        total_studies = self.collection.count_documents({})

        pipeline = [
            {'$unwind': '$protocolSection.designModule.phases'},
            {'$group': {
                '_id': '$protocolSection.designModule.phases',
                'count': {'$sum': 1}
            }}
        ]
        results = list(self.collection.aggregate(pipeline))

        phase_percentages = []
        for r in results:
            phase = r["_id"]
            count = r["count"]
            percentage = (count / total_studies) * 100 if total_studies > 0 else 0  
            phase_percentages.append({"phase": phase, "percentage": percentage})

        response_dict = {"phase_percentages": phase_percentages}

        return response_dict




