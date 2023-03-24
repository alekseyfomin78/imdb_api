from imdb_api.celery import app
from api.utils.send_email import send_email


@app.task
def send_email_task(mail_subject: str, message: str, to_email: str):
    send_email(mail_subject=mail_subject, message=message, to_email=to_email)
