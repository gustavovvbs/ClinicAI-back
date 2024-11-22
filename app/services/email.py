import os
from smtplib import SMTP, SMTPException
from typing import List
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def send_email(email: str, studies: List[dict]):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "siriolibanesinfos@gmail.com"
    sender_password = os.getenv("SENDER_PASSWORD")

    try:
        with SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)

            study_list = "\n".join(
                [f"{i+1}. {study['Title']} - {study['Description']}" for i, study in enumerate(studies)]
            )
            subject = "Lista de Estudos Clínicos Relacionados"
            body = (
                f"Subject: {subject}\n"
                f"Content-Type: text/plain; charset=utf-8\n\n"
                f"Olá,\n\n"
                f"Segue a lista de estudos clínicos relacionados:\n\n"
                f"{study_list}\n\n"
                f"Atenciosamente,\n"
                f"Equipe de Estudos Clínicos"
            )

            server.sendmail(sender_email, email, body.encode("utf-8"))
            print(f"E-mail enviado com sucesso para {email}")

    except SMTPException as e:
        print(f"Erro ao enviar e-mail: {str(e)}")
        raise Exception(f"Erro ao enviar e-mail: {str(e)}")
