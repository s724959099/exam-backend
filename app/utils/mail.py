"""Sending Email by sendgrid"""
import sendgrid
from config import config
from sendgrid.helpers.mail import Content, Email, Mail, To


def send_email(to, subject, message):
    """
    Send Email
    Returns:
        send email response
    """
    sg = sendgrid.SendGridAPIClient(api_key=config.get('SENDGRID_API_KEY'))
    from_email = Email(config.get('SENDGRID_FROM_MAIL'))
    if isinstance(to, list):
        to_email = []
        for el in to:
            to_email.append(el)
    else:
        to_email = To(to)
    content = Content('text/plain', message)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response
