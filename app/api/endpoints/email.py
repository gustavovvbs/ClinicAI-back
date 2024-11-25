from flask import Blueprint, request, jsonify, current_app
from smtplib import SMTPException
from app.services.email import EmailService

email_bp = Blueprint("email", __name__)

@email_bp.route("/send", methods=["POST"])
def send_email_endpoint():
    try:
        email_service = EmailService()
        data = request.get_json()

        email = data.get("email")
        studies = data.get("studies", [])
        if not email or not studies:
            current_app.logger.error("Missing email or studies.")
            return jsonify({"error": "Missing email or studies."}), 400

        service_response = email_service.send_email(email, studies)
        return jsonify({"message": service_response}), 200

    except SMTPException as e:
        current_app.logger.error(f"Error sending the email: {str(e)}")
        return jsonify({"error": f"error sending the email: {str(e)}"}), 503

    except Exception as e:
        current_app.logger.error(f"Error sending the email: {str(e)}")
        return jsonify({"error": str(e)}), 500