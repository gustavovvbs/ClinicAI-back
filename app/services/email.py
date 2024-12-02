import os
from smtplib import SMTP, SMTPException
from typing import List
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "siriolibanesinfos@gmail.com"
        self.sender_password = os.getenv("SENDER_PASSWORD")

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
                server.login(self.sender_email, self.sender_password)

                message = MIMEMultipart("alternative")
                message["Subject"] = "Lista de Estudos Clínicos Relacionados"
                message["From"] = self.sender_email
                message["To"] = email
                
                study_list_items = ""
                for i, study in enumerate(studies):
                    locations = study.get("Location", [])
                    location_str = "No location available"
                    if locations and isinstance(locations, list) and len(locations) > 0:
                        first_loc = locations[0]
                        location_str = f"{first_loc.get('City', 'N/A')} - {first_loc.get('Country', 'N/A')}"

                    contacts = study.get("Contacts", [])
                    contacts_str = "No contacts available"
                    if contacts and isinstance(contacts, list) and len(contacts) > 0:
                        for contact in contacts:
                            if isinstance(contact, dict):
                                contacts_str = f"{contact.get('name', 'N/A')} - {contact.get('email', 'N/A')}"
                                break
                            else:
                                contacts_str = contact

                    study_list_items += f"""
                    <h2>{i+1}. {study.get("Title", "Sem título")}</h2>
                    <p><strong>Condições:</strong> {", ".join(study.get("Conditions", ["Sem condições informadas"]))}</p>
                    <p><strong>Instituição:</strong>: {study.get("Organization", "Sem instituição informada")}</p>
                    <p><strong>Descrição:</strong>: {study.get("Description", "Sem descrição informada")}</p>
                    <p><strong>Intervenções</strong>: {",".join(study.get("InterventionNames", []))}</p>
                    <p><strong>Localização</strong>: {location_str}</p>
                    <p><strong>Contatos</strong>: {contacts_str} </p>
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

                part = MIMEText(body, "html")
                message.attach(part)
                
                server.send_message(message)
                return "Email sent successfully"

        except SMTPException as e:
            raise Exception(f"error sending email: {str(e)}")

