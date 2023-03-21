from django.core.mail import EmailMessage


def sent_email(mail_subject: str, message: str, to_email: str):
    email = EmailMessage(subject=mail_subject, body=message, to=[to_email])
    email.send()
