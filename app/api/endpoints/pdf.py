from io import BytesIO
from flask import request, jsonify, Blueprint, current_app, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

pdf_bp = Blueprint("pdf", __name__)


def wrap_text(c, text, x, y, max_width, line_height, page_height, font="Helvetica", font_size=12):
    """
    Função para quebrar texto automaticamente e desenhar no PDF.
    """
    c.setFont(font, font_size)
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        # Calcula a largura da linha com a fonte especificada
        if c.stringWidth(current_line + " " + word, font, font_size) > max_width:
            lines.append(current_line)
            current_line = word
        else:
            current_line += " " + word
    lines.append(current_line)  # Adiciona a última linha

    for line in lines:
        # Verifica se há espaço suficiente na página
        if y < 50:
            c.showPage()
            y = page_height - 50
            c.setFont(font, font_size)

        c.drawString(x, y, line.strip())
        y -= line_height

    return y



@pdf_bp.route("/generate", methods=["POST"])
def generate_pdf():
    try:
        # Recebe os dados do corpo da requisição
        data = request.get_json()

        # Valida se 'studies' está presente e é uma lista
        if not data or not isinstance(data, dict) or "studies" not in data:
            return jsonify({"error": "'studies' deve ser fornecido no corpo da requisição"}), 400

        studies = data["studies"]

        # Verifica se 'studies' é uma lista
        if not isinstance(studies, list):
            return jsonify({"error": "'studies' deve ser uma lista"}), 400

        # Cria o buffer para o PDF
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter

        # Itera sobre cada estudo para criar um "slide" (página)
        for study in studies:
            # Verifica se cada estudo é um dicionário
            if not isinstance(study, dict):
                continue  # Ignora elementos que não são dicionários

            # Título do Slide
            c.setFont("Helvetica-Bold", 20)
            text_start_y = wrap_text(c, "Relatório de Estudos Clínicos", 50, height - 50, 500, 20, height)

            # Título do Estudo
            title = study.get("Title", "Sem título")
            c.setFont("Helvetica-Bold", 16)
            text_start_y = wrap_text(c, f"Título: {title}", 50, text_start_y - 20, 500, 20, height)

            # Descrição
            description = study.get("Description", "Sem descrição")
            c.setFont("Helvetica", 12)
            c.drawString(50, text_start_y, "Descrição:")
            text_start_y = wrap_text(c, description, 50, text_start_y - 20, 500, 15, height)

            # Localização
            location = study.get("Location", [{}])
            if isinstance(location, list) and len(location) > 0 and isinstance(location[0], dict):
                city = location[0].get("City", "N/A")
                country = location[0].get("Country", "N/A")
                text_start_y = wrap_text(c, f"Localização: {city}, {country}", 50, text_start_y - 20, 500, 15, height)

            # Contatos
            contact = study.get("Contacts", [])
            if isinstance(contact, list):
                for contact_item in contact:
                    if isinstance(contact_item, dict):
                        contact_name = contact_item.get("name", "N/A")
                        contact_email = contact_item.get("email", "N/A")
                        contact_phone = contact_item.get("phone", "N/A")
                        contact_text = f"Contato: {contact_name} | {contact_email} | {contact_phone}"
                        text_start_y = wrap_text(c, contact_text, 50, text_start_y - 20, 500, 15, height)

            # Datas
            start_date = study.get("StartDate", "N/A")
            end_date = study.get("endDate", "N/A")
            if isinstance(start_date, dict):
                start_date = start_date.get("date", "N/A")
            if isinstance(end_date, dict):
                end_date = end_date.get("date", "N/A")
            text_start_y = wrap_text(c, f"Datas: Início - {start_date}, Término - {end_date}", 50, text_start_y - 30, 500, 15, height)

            # Próxima página
            c.showPage()

        # Finaliza o PDF
        c.save()
        pdf_buffer.seek(0)

        # Retorna o PDF gerado
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name="relatorio_estudos.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar PDF: {e}")
        return jsonify({"error": "Erro interno ao gerar PDF"}), 500
