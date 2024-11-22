from flask import Blueprint, request, jsonify
from app.services.email import send_email

email_bp = Blueprint("email", __name__)

@email_bp.route("/send", methods=["POST"])
def send_email_endpoint():
    try:
        data = request.get_json()

        # Validação dos campos
        email = data.get("email")
        studies = data.get("studies", [])
        if not email or not studies:
            return jsonify({"error": "E-mail ou lista de estudos ausente"}), 400

        # Envio do e-mail
        send_email(email, studies)
        return jsonify({"message": "E-mail enviado com sucesso!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500