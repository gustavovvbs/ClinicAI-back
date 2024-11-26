import pytest 
from unittest.mock import MagicMock, patch 
from app.services.search  import SearchService
from app.schemas.search import MedicoSearch, PacienteSearch
from requests.exceptions import HTTPError

def test_search_paciente():

    mock_translate_service = MagicMock()
    mock_translate_service.translate_fields.side_effect = lambda x: x

    service = SearchService(translate_service=mock_translate_service)
    
    #mocking paciente search 
    search_data = PacienteSearch(
        condition = "cancer",
        keywords = "",
        age = "adult",
        intervention = "",
        status = ["RECRUITING"],
        location = "Recife, PE"
    )

    with patch("app.services.search.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200 
        mock_response.json.return_value = {"studies": []}

        mock_get.return_value = mock_response 

        results = service.search_paciente(
            search_data,
            page_size=1,
            page='1'
        )

        assert results == {
            "studies": [],
            "currentPage": 1,
            "totalPages": 1,
        }

        expected_params = {
            "format": "json",
            "pageSize": 1,
            "filter.advanced": "AREA[MaximumAge]RANGE[18 years, 64 years]",
            "filter.overallStatus": "RECRUITING",
            "query.locn": "Recife",
            "query.cond": "cancer"
        }

        mock_get.assert_called_once_with(
            service.BASE_URL,
            params=expected_params,
        )

def test_filter_by_specific_location():
    
    mock_translate_service = MagicMock()
    mock_translate_service.translate_fields.side_effect = lambda x: x

    service = SearchService(translate_service=mock_translate_service)

    studies = [
        {
            'Title': 'Study in New York',
            'Location': [
                {
                    'City': 'New York',
                }
            ]
        },
        {
            'Title': 'Study in Boston',
            'Location': [
                {
                    'City': 'Boston',
                }
            ]
        }
    ]

    results = service.filter_by_location(studies, "New York")
    
    assert len(results) == 1
    assert results[0]["Title"] == "Study in New York"

def test_medico_search():
    
    mock_translate_service = MagicMock()
    mock_translate_service.translate_fields.side_effect = lambda x: x

    service = SearchService(translate_service=mock_translate_service)

    search_data = MedicoSearch(
        title="Diabetes Study",
        keywords="",
        age="adult",
        studyPhase="PHASE3",
        hasResults=True,
        acceptsHealthyVolunteers=False,
        sex='female',
        studyType='INTERVENTIONAL',
        organization='UFPE',
        studyId='NCT01234567'
    )

    with patch('app.services.search.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200 
        mock_response.json.return_value = {"studies": []}

        mock_get.return_value = mock_response

        results = service.search_medico(
            search_data,
            page_size = 1, 
            page = '1'
        )

        assert results == {
            'studies': [],
            "currentPage": 1,
            "totalPages": 1,
        }

        expected_params = {
            'format': 'json',
            'pageSize': 1,
            'aggFilters': 'healthy:n,results:y,sex:female',
            'filter.advanced': 'AREA[ResponsiblePartyOldOrganization]UFPE AND AREA[MaximumAge]RANGE[18 years, 64 years] AND AREA[Phase]PHASE3 AND AREA[StudyType]INTERVENTIONAL AND AREA[NCTId]NCT01234567',
            'query.titles': 'Diabetes Study',
        }

        mock_get.assert_called_once_with(service.BASE_URL, params=expected_params)


