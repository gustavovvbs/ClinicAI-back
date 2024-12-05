from io import BytesIO
from flask import request, jsonify, Blueprint, current_app, send_file
from reportlab.pdfgen import canvas

pdf_bp = Blueprint("pdf", __name__)

@pdf_bp.route("/generate", methods=["POST"])
def generate_pdf():
    try:
        # Recebe os dados do corpo da requisição
        data = request.get_json()
        pdf_buffer = BytesIO()
        
        # Cria o PDF
        c = canvas.Canvas(pdf_buffer)
        c.drawString(100, 750, "Relatório de Estudos Clínicos")
        
        # Adiciona informações do JSON ao PDF
        y = 720
        for key, value in data.items():
            c.drawString(100, y, f"{key}: {value}")
            y -= 20  # Move para a próxima linha
        
        c.save()

        # Retorna o PDF como resposta
        pdf_buffer.seek(0)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name="relatorio_estudos.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        current_app.logger.error(f"Error generating PDF: {e}")
        return jsonify({"error": "internal server error"}), 500