import os
from smtplib import SMTP, SMTPException
from typing import List
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 

# Carregar variáveis de ambiente
load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "siriolibanesinfos@gmail.com"
        sender_password = os.getenv("SENDER_PASSWORD")

    def send_email(self, email: str, studies: List[dict]):
        """
        Send an email with a list of studies to a recipient.

        Args:
            email (str): The recipient's email address.
            studies (List[dict]): A list of studies to send.

        Returns:
            str: Message with the result of the operation
        """
        try:
            with SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, sender_password)

                study_list_items = ""
                for i, study in enumerate(studies):
                    study_list_items += f"""
                    <h2>{i+1}. {study.get("Title", "Sem título")}</h2>
                    <p><strong>Condições:</strong>: {",".join(study.get("Conditions", "Sem condições informadas"))}</p>
                    <p><strong>Instituição:</strong>: {study.get("Organization", "Sem instituição informada")}</p>
                    <p><strong>Descrição:</strong>: {study.get("Description", "Sem descrição informada")}</p>
                    <p><strong>Intervenções</strong>: {",".join(study.get("InterventionNames", []))}</p>
                    <p><strong>Localização</strong>: {",".join(study.get("Location", []))}</p>
                    <p><strong>Contatos</strong>: {",".join(study.get("Contacts", []))}</p>
                    <p><strong>Restrições</strong>: {study.get("Restrictions", "Sem restrições informadas")}</p>
                    <hr>
                    """

                subject = "Lista de Estudos Clínicos Relacionados"
                body = f"""
                <html>
                   <body>
                        <h1>Lista de Estudos Clínicos Relacionados</h1>
                        <p>Olá,</p>
                        <p>Segue a lista de estudos clínicos relacionados:</p>
                        {study_list_items}
                        <p>Atenciosamente,</p>
                        <p>Equipe de Pesquisa e Inovação, Hospital Sírio-Libanês.</p>
                    </body>
                </html>
                """
                server.sendmail(self.sender_email, email, body.encode("utf-8"))

                return "Email sent successfully"

        except SMTPException as e:
            raise Exception(f"error sending email: {str(e)}")

