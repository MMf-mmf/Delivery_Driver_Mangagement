from twilio.rest import Client
from django.conf import settings


def send_gps_error_message(user):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    response = client.messages.create(
        body=f'Could Not Get GPS Location From {user.username}', 
        to=settings.DEV_PHONE_NUMBER, from_=settings.TWILIO_PHONE_NUMBER)
    return response