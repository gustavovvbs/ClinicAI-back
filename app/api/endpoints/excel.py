from app.services.excel import ExcelService
from flask import request, jsonify, Blueprint, current_app, send_file
from io import BytesIO

excel_bp = Blueprint("excel", __name__)

@excel_bp.route("/fetch", methods=["POST"])
def fetch_excel():
    try:
        # Obtém os dados da requisição
        data = request.get_json()

        # Cria o serviço Excel
        excel_service = ExcelService()
        excel_bin = excel_service.get_excel(data)

        # Retorna o arquivo Excel
        return send_file(
            BytesIO(excel_bin),
            as_attachment=True,
            download_name="estudos_clinicos.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar Excel: {e}")
        return jsonify({"error": "Erro interno ao gerar Excel"}), 500
