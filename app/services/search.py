from typing import Optional, List, Dict, Any
import requests
from flask import current_app
from app.schemas.search import PacienteSearch
from app.schemas.search import MedicoSearch
from app.services.translate import TranslateService

class SearchService:
    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

    def __init__(self, translate_service = None):
        self.translate_service = translate_service or TranslateService()
        self.AGE_MAPPING = {
        "child": ("0 years", "17 years"),
        "adult": ("18 years", "64 years"),
        "senior": ("65 years", "200 years")
        }

    @staticmethod
    def filter_studies(api_response: Dict[str, Any], search_data) -> List[Dict[str, Any]]:
        """
        Performs a GIANT filtering through the api response to get the fields we are interested in (dont ever try to understand this function lol)
        Args:
            api_response (dict): The response from the API endpoint.
        Returns:
            list: The filtered studies.
        """
        data_dict = search_data.model_dump(exclude_none=True, exclude_unset=True)
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
                if loc.get("status") == data_dict["status"][0]:
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

    def search_paciente(
        self,
        search_data: PacienteSearch,
        page_size: int = 3,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """ 
        Searches for studies based on the provided search fields. (only basic fields for the Paciente search)

        Args:
            search_data (PacienteSearch): The search fields to filter the studies.
            fields (list): The fields to include in the results.
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

        if any(key in data_dict for key in ['age']):
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
        return self._paginate_results(
            search_url=search_url,
            params=params,
            target_page=page,
            page_translator = self.translate_service,
            search_data=search_data
        )

    def search_medico(
        self, 
        search_data: MedicoSearch,
        page_size: int = 3,
        page: int = 1
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
        return self._paginate_results(
            search_url=search_url,
            params=params,
            target_page=page,
            page_translator = self.translate_service,
            search_data = search_data
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
        target_page: int,
        page_translator: None ,
        search_data = None
    ):
        """
        Paginates through the API page results until the target page is reached.
        Args:
            search_url (str): The URL of the API endpoint to search.
            params (dict): The query parameters to include in the API request.
            target_page (int): The page number to retrieve.
            page_translator (None): An optional translator to apply to the results.
        Returns:
            list: The filtered results from the target page, or an empty list if the target page is not reached.
        Raises:
            Exception: If the API request fails or returns a non-200 status code.

        notes: it will make a request to the CT api target_page times, even though the data from these 'on the way' requests are not processed or filtered, it might be a point to be cautious about in the case of a high target page number
        """
        current_page = 1
        next_page_token = None 

        while current_page <= target_page:
            if next_page_token: 
                params["pageToken"] = next_page_token
            
            response = requests.get(search_url, params = params)
            if response.status_code != 200:
                self.handle_api_error(response)

            api_response = response.json()

            if current_page == target_page:
                filtered_response = self.filter_studies(api_response=api_response, search_data=search_data)
                filtered_response = self.filter_by_location(studies=filtered_response, location=params.get("query.locn", ""))
                if page_translator:
                    filtered_response = page_translator.translate_fields(filtered_response)
                return filtered_response

            next_page_token = api_response.get("nextPageToken")
            if not next_page_token:
                break

            current_page += 1

        return []

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
