from app.services.excel import ExcelService 
from io import BytesIO
from flask import request, jsonify, Blueprint, current_app, send_file
from app.core.validation_middleware import validate_json 
from app.schemas.study import CreateStudySchema

excel_bp = Blueprint("excel", __name__)

@excel_bp.route("/fetch", methods=["POST"])
def fetch_excel():
    try:
        data = request.get_json()
        excel_service = ExcelService()
        excel_bin = excel_service.get_excel(data)
        return send_file(
            BytesIO(excel_bin),
            as_attachment=True,
            download_name="estudos_clinicos.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        current_app.logger.error(f"Error fetching excel: {e}")
        return jsonify({"error": "internal server error"}), 500

