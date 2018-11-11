#!/usr/bin/env python
#  -*- coding: utf-8 -*-

# 3rd party imports ------------------------------------------------------------
from flask import Flask, request
from webexteamssdk import WebexTeamsAPI, Webhook

# local imports ----------------------------------------------------------------
from helpers import (read_yaml_data,
                     get_ngrok_url,
                     find_webhook_by_name,
                     delete_webhook, create_webhook)
from twilio_contacts import *
from twilio_sendMsg import send_text_message
# import traceback


flask_app = Flask(__name__)
teams_api = None


# def wrapped_func_call(room, func, args=[], kwargs={}):
#     try:
#         # teams_api.messages.create(room.id, text="...")
#         return func(*args, room=room, **kwargs)
#     except Exception:
#         msg = "```\n```\n".format(traceback.format_exc())
#         teams_api.messages.create(room.id, markdown=msg)
#         raise
#     return 'tmp'



@flask_app.route('/teamswebhook', methods=['POST'])
def teamswebhook():
    if request.method == 'POST':

        json_data = request.json
        print("\n")
        print("WEBHOOK POST RECEIVED:")
        print(json_data)
        print("\n")

        webhook_obj = Webhook(json_data)
        # Details of the message created
        room = teams_api.rooms.get(webhook_obj.data.roomId)
        message = teams_api.messages.get(webhook_obj.data.id)
        person = teams_api.people.get(message.personId)
        email = person.emails[0]

        print("NEW MESSAGE IN ROOM '{}'".format(room.title))
        print("FROM '{}'".format(person.displayName))
        print("MESSAGE '{}'\n".format(message.text))

        # Message was sent by the bot, do not respond.
        # At the moment there is no way to filter this out, there will be in the future
        me = teams_api.people.me()
        if message.personId == me.id:
            return 'OK'
        else:
            msg = message.__getattr__('text')
            print('Message extracted is', msg)
            msg = msg.split(' ')
            print(msg)

            if 'SMS' == msg[1]:
                if msg[2] in person_dict:
                    msgToSend = ' '.join(msg[3:])
                    print(msgToSend)
                    send_text_message(msg[2], person_dict.get(msg[2]), msgToSend)
                    teams_api.messages.create(room.id, text='Message successfully delivered to' + str(msg[2]))
            elif 'VOICEMSG' == msg[1]:
                if msg[2] in person_dict:
                    # msgToSend = ' '.join(msg[3:])
                    # print(msgToSend)
                    send_text_message(msg[2], person_dict.get(msg[2]))
                    teams_api.messages.create(room.id, text='Voice message successfully delivered to' + str(msg[2]))
            else:
                teams_api.messages.create(room.id, text='hello, okay '+str(email))

    else:
        print('received none post request, not handled!')


if __name__ == '__main__':
    config = read_yaml_data('/opt/config/config.yaml')['hello_bot']
    teams_api = WebexTeamsAPI(access_token=config['teams_access_token'])

    ngrok_url = get_ngrok_url()
    webhook_name = 'hello-bot-wb-hook'
    dev_webhook = find_webhook_by_name(teams_api, webhook_name)

    if dev_webhook:
        delete_webhook(teams_api, dev_webhook)
    create_webhook(teams_api, webhook_name, ngrok_url + '/teamswebhook')

    flask_app.run(host='0.0.0.0', port=5000)
