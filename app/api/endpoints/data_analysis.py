from flask import current_app
from app.services.data_analysis import DataService 
from app.services.search import SearchService
from app.schemas.search import PacienteSearch
from flask import Blueprint, request, jsonify

data_analysis_bp = Blueprint("data_analysis", __name__)

@data_analysis_bp.route("/metrics", methods=["GET"])
def get_metrics():
    try:
        search_service = SearchService()
        data_service = DataService(search_service, current_app.mongo)
        main_diseases_response = data_service.get_main_diseases()
        main_diseases = main_diseases_response["main_diseases"]

        representatividade_response = data_service.get_representatividade()
        representatividade = representatividade_response

        top_centers_response = data_service.get_top_centers()
        top_centers = top_centers_response["top_centers"]

        types_per_centers_response = data_service.get_types_per_centers()
        types_per_centers = types_per_centers_response["types_of_studies_per_center"]

        main_treatments_response = data_service.get_main_treatments()
        main_treatments = main_treatments_response["main_treatments"]

        phase_percentages_response = data_service.get_phase_percentages()
        phase_percentages = phase_percentages_response["phase_percentages"]

        response_dict = {
            "main_diseases": main_diseases,
            "representatividade": representatividade,
            "top_centers": top_centers,
            "types_per_centers": types_per_centers,
            "main_treatments": main_treatments,
            "phase_percentages": phase_percentages,
        }

        return jsonify(response_dict), 200
    except Exception as e:
        return jsonify({"error": f"internal server error {e}"}), 500

