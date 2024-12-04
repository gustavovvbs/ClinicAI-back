import os
import json
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
import pymongo
import requests
from pinecone import Pinecone
from flask import current_app
from bson import ObjectId
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from app.schemas.search import PacienteSearch
from app.schemas.search import MedicoSearch
from app.services.translate import TranslateService

load_dotenv()

class SearchService:
    def __init__(self, translate_service = None):
        self.translate_service = translate_service or TranslateService()
        self.BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
        self.AGE_MAPPING = {
        "child": ("0 years", "17 years"),
        "adult": ("18 years", "64 years"),
        "senior": ("65 years", "200 years")
        }
        self.embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")
        self.db = current_app.mongo 
        self.collection = self.db.studies

        pc = Pinecone()
        index_name = "sprint-hsl"
        index = pc.Index(name = index_name)
        self.vector_store = PineconeVectorStore(index, embedding=self.embeddings_model)

        self.generate_embeddings_for_existing_documents()

    @staticmethod
    def filter_studies(api_response: Dict[str, Any], search_data) -> List[Dict[str, Any]]:
        """
        Performs a GIANT filtering through the api response to get the fields we are interested in (dont ever try to understand this function lol)
        Args:
            api_response (dict): The response from the API endpoint.
        Returns:
            list: The filtered studies.
        """
        if hasattr(search_data, 'model_dump'):
            data_dict = search_data.model_dump(exclude_none=True, exclude_unset=True)
        elif isinstance(search_data, dict):
            data_dict = {
                k: v for k, v in search_data.items()
                if v is not None and (
                    (isinstance(v, (list, dict)) and v) or
                    (isinstance(v, str) and v.strip()) or
                    (not isinstance(v, (str, list, dict)))
                )
            }
   
        filtered_studies = []

        for study in api_response.get("studies", []):
            filtered_study = {}
            protocol_section = study.get("protocolSection", {})
            identification_module = protocol_section.get("identificationModule", {})
            description_module = protocol_section.get("descriptionModule", {})
            arms_interventions_module = protocol_section.get("armsInterventionsModule", {})
            sponsors_collaborators_module = protocol_section.get("sponsorCollaboratorsModule", {})
            contacts_locations_module = protocol_section.get("contactsLocationsModule", {})
            conditions_module = protocol_section.get("conditionsModule", {})
            eligibility_module = protocol_section.get("eligibilityModule", {})
            status_module = protocol_section.get("statusModule", {})
            design_module = protocol_section.get("designModule", {})

            title = identification_module.get("briefTitle") or identification_module.get("officialTitle") or "N/A"
            filtered_study["Title"] = title

            brief_summary = description_module.get("briefSummary", "")
            detailed_description = description_module.get("detailedDescription", "")
            full_description = "\n\n".join(filter(None, [brief_summary, detailed_description])).strip() or "N/A"
            filtered_study["Description"] = full_description

            interventions = []
            intervention_names = [interv.get("name", "N/A") for interv in arms_interventions_module.get("interventions", [])]
            intervention_explanations = [interv.get("description", "N/A") for interv in arms_interventions_module.get("interventions", [])]
            if not intervention_names:
                intervention_names = ["N/A"]
                intervention_explanations = ["N/A"]
            for arm in arms_interventions_module.get("armGroups", []):
                intervention = {
                    "description": arm.get("description", "N/A"),
                    "label": arm.get("label", []),
                    "interventionType": arm.get("type", "N/A")
                }
                interventions.append(intervention)
            if len(intervention_names) < len(interventions):
                for i in range(len(interventions) - len(intervention_names)):
                    intervention_names.append("N/A")
                    intervention_explanations.append("N/A")
            for i, intervention in enumerate(interventions):
                intervention["name"] = intervention_names[i]
                intervention["explanation"] = intervention_explanations[i]
            filtered_study["InterventionNames"] = intervention_names
            filtered_study["Interventions"] = interventions

            sponsor = sponsors_collaborators_module.get("leadSponsor", {}).get("name", "N/A")
            filtered_study["Sponsor"] = sponsor

            researchers = contacts_locations_module.get("overallOfficials", []) or ["N/A"]
            filtered_study["Researchers"] = researchers

            organization = identification_module.get("organization", "N/A")
            filtered_study["FunderType"] = organization.get("class", "N/A")
            filtered_study["Organization"] = organization.get("fullName", "N/A")

            start_date = identification_module.get("startDateStruct", {}).get("date", "N/A")
            filtered_study["StartDate"] = start_date

            completion_date_struct = status_module.get("completionDateStruct", {})
            filtered_study["endDate"] = completion_date_struct

            keywords = conditions_module.get("keywords", [])
            filtered_study["Keywords"] = keywords

            contacts = contacts_locations_module.get("centralContacts", []) or ["N/A"]
            filtered_study["Contacts"] = contacts

            study_type = design_module.get("studyType", "N/A")
            filtered_study["StudyType"] = study_type

            study_phase = design_module.get("phases", "N/A")
            filtered_study["Phase"] = study_phase

            healthy_volunteers = eligibility_module.get("healthyVolunteers", "N/A")
            filtered_study["HealhyVolunteers"] = healthy_volunteers

            sex = eligibility_module.get("sex", "N/A")
            filtered_study["Sex"] = sex 

            minimum_age = eligibility_module.get("minimumAge", "N/A")
            maximum_age = eligibility_module.get("maximumAge", "N/A")
            filtered_study["MinimumAge"] = minimum_age
            filtered_study["MaximumAge"] = maximum_age

            study_start_date = status_module.get("startDateStruct", "N/A")
            filtered_study["StartDate"] = study_start_date

            primary_completion_date = status_module.get("primaryCompletionDateStruct", "N/A")
            filtered_study["PrimaryCompletionDate"] = primary_completion_date

            study_first_submission_date = status_module.get("studyFirstSubmitDate", "N/A")
            filtered_study["FirstSubmissionDate"] = study_first_submission_date

            study_first_post_date = status_module.get("studyFirstPostDateStruct", "N/A")
            filtered_study["FirstPostDate"] = study_first_post_date

            last_update_post_date = status_module.get("lastUpdatePostDateStruct", "N/A")
            filtered_study["LastUpdatePostDate"] = last_update_post_date


            locations = contacts_locations_module.get("locations", [])
            location_info = []
            for loc in locations:
                    if data_dict.get("status") and loc.get("status") in data_dict.get("status"):
                        facility = loc.get("facility", "N/A")
                        city = loc.get("city", "N/A")
                        state = loc.get("state", "N/A")
                        country = loc.get("country", "N/A")
                        status = loc.get("status", "N/A")
                        location_info.append({
                            "Facility": facility,
                            "City": city,
                            "State": state,
                            "Country": country,
                            "Status": status
                        })
                    else:
                        facility = loc.get("facility", "N/A")
                        city = loc.get("city", "N/A")
                        state = loc.get("state", "N/A")
                        country = loc.get("country", "N/A")
                        status = loc.get("status", "N/A")
                        location_info.append({
                            "Facility": facility,
                            "City": city,
                            "State": state,
                            "Country": country,
                            "Status": status
                        })

            filtered_study["Location"] = location_info or ["N/A"]

            conditions = conditions_module.get("conditions", []) or ["N/A"]
            filtered_study["Conditions"] = conditions

            restrictions = eligibility_module.get("eligibilityCriteria", "N/A").strip()
            filtered_study["Restrictions"] = restrictions

            has_results = study.get("hasResults", False)
            filtered_study["Has Results Published"] = has_results

            filtered_studies.append(filtered_study)

        return filtered_studies

    def flatten_metadata(self, doc: dict) -> dict:
        """Flatten nested objects and convert to Pinecone-compatible format"""
        flattened = {}
        
        for key, value in doc.items():
            if isinstance(value, (str, int, float, bool)):
                flattened[key] = value
            elif isinstance(value, list):
                flattened[key] = json.dumps(value)
            elif isinstance(value, dict):
                flattened[key] = json.dumps(value)
            else:
                flattened[key] = str(value)
                
        return flattened

    def generate_embeddings_for_existing_documents(self):
        documents = list(self.collection.find({'embedding': {'$exists': False}}))
        if not documents:
            documents = list(self.collection.find({'embedding': False}))
            if not documents:
                return 
            
        for doc in documents:
            doc['_id'] = str(doc['_id'])
            metadata = self.flatten_metadata(doc)
            
            doc = Document(
                page_content=(
                    f"{metadata['Title']} {metadata['Description']} "
                    f"{' '.join(metadata['Conditions'])}"
                ).strip(),
                metadata=metadata
            )

            _id = [str(doc.metadata["_id"])]

            self.vector_store.add_documents([doc], ids=_id)
            
            self.collection.update_one(
                {"_id": ObjectId(doc.metadata["_id"])},
                {"$set": {"embedding": True}}
            )

        return "Generated embeddings for existing documents."

    def search_by_similarity(self, query_text, location=None, top_k=4, similarity_threshold=0.2):
        """ 
        Performs a similarity search on the existing studies embeddings 

        Args: 
            query_text (str): The text to search for.
            location (str): The location to filter the results.
            top_k (int): The number of results to return.
            similarity_threshold (float): The minimum similarity score to consider a result. (it is still a bit arbitrary, there is room for experimentation here)

        Returns:
            list: The top k results from the similarity search.
        """
        results = self.vector_store.similarity_search_with_score(
            query_text,
            k = top_k,
            filter={"sub_status": "accepted"}
        )

        filtered_results = []
        for result, score in results:
            if score > similarity_threshold:
                result.metadata.Location = json.dumps(result.metadata.Location)
                filtered_results.append(result.metadata)

        return filtered_results

    def search_paciente(
        self,
        search_data: PacienteSearch,
        page_size: int = 3,
        page: str = '1'
    ) -> List[Dict[str, Any]]:
        """ 
        Searches for studies based on the provided search fields and embeddings.

        Args:
            search_data (PacienteSearch): The search fields to filter the studies.
            page_size (int): The number of results to return per page.
            page (int): The page number to retrieve.

        Returns:
            list: The combined results from embedding search and API search.
        """
        query_text = ''
        if search_data.condition:
            query_text = ' '.join(search_data.condition)
        elif search_data.keywords:
            query_text = search_data.keywords
        elif search_data.condition and search_data.keywords:
            query_text = f"{search_data.condition} {search_data.keywords}"

        embedding_results = self.search_by_similarity(
            query_text=query_text,
            location=search_data.location,
            top_k=page_size
        )

        search_url = self.BASE_URL
        params = {
            "format": "json",
            "pageSize": page_size
        }

        data_dict = search_data.model_dump(exclude_none=True, exclude_unset=True)

        if 'age' in data_dict:
            if data_dict["age"] in self.AGE_MAPPING:
                age_value = data_dict.pop('age')
                age_range = self.AGE_MAPPING[age_value]
                age_expr = f"AREA[MaximumAge]RANGE[{age_range[0]}, {age_range[1]}]"
                params['filter.advanced'] = age_expr

        for key, value in data_dict.items():
            alias = search_data.model_fields[key].alias
            if isinstance(value, list):
                params[alias] = ",".join(value)
            else:
                params[alias] = value

        if "query.locn" in params:
            params["query.locn"] = params["query.locn"].split(",")[0].strip()

        target_page = page
        if "page" in params:
            target_page = params.pop("page")

        api_results = self._paginate_results(
            search_url=search_url,
            params=params,
            target_page=target_page,
            page_translator=self.translate_service,
            search_data=data_dict,
            page_size=page_size
        )

        api_studies = api_results.get("studies", [])

        combined_results = self.combine_results(embedding_results, api_studies)

        response_dict = {
            "studies": combined_results,
            "totalPages": api_results.get("totalPages"),
            "currentPage": api_results.get("currentPage")
        }

        return response_dict

    def combine_results(self, embedding_results, api_results):
        """
        Combine the results from embedding search and API search.

        Args:
            embedding_results (list): The results from embedding search.
            api_results (list): The results from API search.

        Returns:
            list: The combined results without duplicates.
        """
        seen_titles = set()
        combined_results = []

        for study in embedding_results:
            title = study.get("Title")
            if title and title not in seen_titles:
                combined_results.append(study)
                seen_titles.add(title)

        for study in api_results:
            title = study.get("Title")
            if title and title not in seen_titles:
                combined_results.append(study)
                seen_titles.add(title)

        return combined_results

    def search_medico(
        self, 
        search_data: MedicoSearch,
        page_size: int = 3,
        page: str = '1'
    ):
        """ 
        Searches for studies based on the provided search fields. (more detailed fields in the Medico search)

        Args:
            search_data (MedicoSearch): The search fields to filter the studies.
            page_size (int): The number of results to return per page.
            page (int): The page number to retrieve.
        Returns:
            list: The filtered results from the target page, or an empty list if there are no results for the query.
        """
        search_url = self.BASE_URL

        params = {
            "format": "json",
            "pageSize": page_size
        }

       
        data_dict = search_data.model_dump(exclude_none=True, exclude_unset=True)
    
        agg_filters = self._construct_agg_filters(data_dict)
        if agg_filters:
            params["aggFilters"] = agg_filters

        advanced_filters = self._construct_advanced_filters(data_dict)
        if advanced_filters:
            params["filter.advanced"] = advanced_filters
    
        for key, value in data_dict.items():
            alias = search_data.model_fields[key].alias
            if isinstance(value, list):
                params[alias] = ",".join(value)
            else:
                params[alias] = value

        if "query.locn" in params:
            params["query.locn"] = params["query.locn"].split(",")[0].strip()
        if "page" in params:
            target_page = params.pop("page")

            return self._paginate_results(
                search_url=search_url,
                params=params,
                target_page=target_page,
                page_translator = self.translate_service,
                search_data = data_dict,
                page_size = page_size
            )

        return self._paginate_results(
            search_url=search_url,
            params=params,
            target_page = page,
            page_translator = self.translate_service,
            search_data = data_dict
        )

    def advanced_search(
        self,
        search_query: str,
        page_size: int = 3,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Performs an advanced search using the provided query string

        Args:
            search_query (str): The advanced search query string
            page_size (int): The number of results to return per page
            page (int): The page number to retrieve
        Returns:
            list: The filtered results from the target page, or an empty list if there are no results for the query
        """
        search_url = self.BASE_URL
        params = {
            "format":"json",
            "pageSize": page_size,
            "filter.advanced": search_query
        }

        return self._paginate_results(
            search_url=search_url,
            params=params,
            target_page=page,   
            page_translator = self.translate_service,
        )

    def filter_by_location(
        self,
        studies: List[Dict[str, Any]],
        location: str) -> List[Dict[str, Any]]:
        """
        Filters the studies by location.

        Args:
            studies (list): The list of studies to filter.
            location (str): The location to filter by.
        Returns:
            list: The filtered studies.
        """
        filter_city = location.split(",")[0].strip().lower()
        filtered_studies = []

        for study in studies:
            for loc in study["Location"]:
                if isinstance(loc, dict):
                    city = loc.get("City", "").lower()
                    if filter_city in city or filter_city == city:
                        study["Location"] = [loc]
                        filtered_studies.append(study)
                        break

        return filtered_studies

    def _paginate_results(
        self, 
        search_url: str,
        params: dict, 
        target_page: str,
        page_translator: Optional[TranslateService] = None,
        search_data: dict = None,
        page_size: Optional[int] = 3
    ):
        """
        Paginates through the API page results until the target page is reached.
        Args:
            search_url (str): The URL of the API endpoint to search.
            params (dict): The query parameters to include in the ct api request. (not exactly the same as the search_data, cause it masks the fields into query syntax)
            target_page (int): The page number to retrieve.
            page_translator (None): An optional translator to apply to the results.
            search_data (dict): The search data to filter the results.
        Returns:
            list: The filtered results from the target page, or an empty list if the target page is not reached.
        Raises:
            Exception: If the API request fails or returns a non-200 status code.

        notes: it will make a request to the CT api target_page times, even though the data from these 'on the way' requests are not processed or filtered, it might be a point to be cautious about in the case of a high target page number
        """
        try:
            target_page = int(target_page)
            if target_page < 1:
                raise ValueError("the target page must be a positive integer")
        except ValueError:
            raise ValueError("invalid target page. the target page must be a positive integer")
        current_page = 1
        next_page_token = None 
        response_dict = {}
        # only the first request will count the total studies, so im doing this to only store the total studies number at the first request
        first_time = False
        total_studies = 0


        while current_page <= target_page:
            if next_page_token:
                first_time = False
                params["pageToken"] = next_page_token
            else:
                first_time = True
                params.pop("pageToken", None)
            params["countTotal"] = "true"

            response = requests.get(self.BASE_URL, params=params)
            if response.status_code != 200:
                self.handle_api_error(response)

            response_data = response.json()
            if first_time:
                total_studies = response_data.get("totalCount", page_size)
            total_pages = (total_studies + page_size - 1) // page_size
            if total_studies <= page_size:
                total_pages = 1
            if total_studies == 0:
                return {
                    "studies": [],
                    "totalPages": total_pages,
                    "currentPage": current_page
                }

            if target_page > total_pages:
                return {
                    "studies": [],
                    "totalPages": total_pages,
                    "currentPage": current_page
                }

            if current_page == target_page:
                filtered_response = self.filter_studies(api_response = response_data, search_data=search_data)
                location = params.get("query.locn", "")
                if location:
                    filtered_response = self.filter_by_location(studies=filtered_response, location=location)
                if page_translator:
                    filtered_response = page_translator.translate_fields(filtered_response)

                response_dict["studies"] = filtered_response
                response_dict["totalPages"] = total_pages
                response_dict["currentPage"] = current_page
                return response_dict

            next_page_token = response_data.get("nextPageToken")
            if not next_page_token:
                return []

            if current_page > target_page:
                break 

            current_page += 1

        return {
            "studies": [],
            "totalPages": total_pages,
            "currentPage": current_page
        }


    def _construct_agg_filters(self, data_dict: Dict[str, Any]) -> Optional[str]:
        accepts_healthy_volunteers = data_dict.pop("acceptsHealthyVolunteers", None)
        has_results = data_dict.pop("hasResults", None)
        sex = data_dict.pop("sex", None)
        
        if sex == "all":
            sex = None

        filters = []
        if accepts_healthy_volunteers is not None:
            filters.append("healthy:y" if accepts_healthy_volunteers else "healthy:n")
        if has_results is not None:
            filters.append("results:y" if has_results else "results:n")
        if sex:
            filters.append(f"sex:{sex}")
        
        return ",".join(filters) if filters else None

    def _construct_advanced_filters(self, data_dict: Dict[str, Any]) -> Optional[str]:
        search_expr_parts = []
        age_value = data_dict.pop('age', None)
        org_value = data_dict.pop('organization', None)
        phase_value = data_dict.pop('studyPhase', None)
        type_value = data_dict.pop('studyType', None)
        id_value = data_dict.pop('studyId', None)

        if org_value:
            search_expr_parts.append(f"AREA[ResponsiblePartyOldOrganization]{org_value}")

        if age_value in self.AGE_MAPPING:
            age_range = self.AGE_MAPPING[age_value]
            search_expr_parts.append(f"AREA[MaximumAge]RANGE[{age_range[0]}, {age_range[1]}]")

        if phase_value in {"NA", "EARLY_PHASE1", "PHASE1", "PHASE2", "PHASE3", "PHASE4"}:
            search_expr_parts.append(f"AREA[Phase]{phase_value}")

        if type_value in {"EXPANDED_ACCESS", "INTERVENTIONAL", "OBSERVATIONAL"}:
            search_expr_parts.append(f"AREA[StudyType]{type_value}")

        if id_value:
            search_expr_parts.append(f"AREA[NCTId]{id_value}")

        search_expr = " AND ".join(search_expr_parts)

        return search_expr


    @staticmethod
    def handle_api_error(response: requests.Response):
        """
        Raises an exception with details about the API error response.

        Args:
            response (requests.Response): The response object from the API request.
        Raises:
            requests.exceptions.HTTPError: If the API response status code is not 200.
        """
        try:
            error_details = response.json()
        except ValueError:
            error_details = response.text
        raise requests.exceptions.HTTPError(
            f"{response.status_code} Client Error: {response.reason} for url: {response.url}\nDetails: {error_details}",
            response=response
        )
