from twilio_keys import *
from twilio.rest import Client


client = Client(account_sid, auth_token)


def send_voice_msg(name, phone_num):
    client.calls.create(
        url='http://demo.twilio.com/docs/voice.xml',
        to=phone_num,
        from_=twilio_number
    )

    print('Voice message sent to', name)