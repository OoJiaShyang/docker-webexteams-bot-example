from twilio_keys import *
from twilio.rest import Client


client = Client(account_sid, auth_token)


def send_text_message(name, phone_num, msg):
    message = client.messages.create(
        to = phone_num,
        from_= twilio_number,
        body = msg)

    print('Message sent to +', name)
