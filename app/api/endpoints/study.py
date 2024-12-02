from flask import Blueprint, request, jsonify
from app.core.validation_middleware import validate_json
from app.core.auth_middleware import validate_token
from app.schemas.study import CreateStudySchema 
from app.services.study import StudyService
from app.services.auth import AuthService

study_bp = Blueprint("study", __name__)

@study_bp.route("/", methods=["POST"])
@validate_json(CreateStudySchema)
def create_study(data):
    # try:
    study_service = StudyService()
    created_study_id = study_service.create_study(data)
    return jsonify({"message": f"Study created successfully with id {created_study_id}"}), 201
    # except Exception as e:
    #     return jsonify({"error": f"internal server error {e}"}), 500

@study_bp.route("/approve/<study_id>", methods=["PUT"])
@validate_token
def approve_study(study_id):
    try:
        study_service = StudyService()
        message = study_service.approve_study(study_id)
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": f"internal server error {e}"}), 500

@study_bp.route("/", methods=["GET"])
@validate_token
def get_studies():
    try:
        status = request.args.get('status')
        study_service = StudyService()
        if status:
            studies = study_service.get_studies(status=status)
        else:
            studies = study_service.get_studies()
        return jsonify({"studies": studies}), 200
    except Exception as e:
        return jsonify({"error": f"internal server error {e}"}), 500

@study_bp.route("/reject/<study_id>", methods=["PUT"])
@validate_token
def reject_study(study_id):
    try:
        study_service = StudyService()
        message = study_service.reject_study(study_id)
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": f"internal server error {e}"}), 500

