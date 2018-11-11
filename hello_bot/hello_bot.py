#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from duckduckpy import query

# 3rd party imports ------------------------------------------------------------
from flask import Flask, request
from webexteamssdk import WebexTeamsAPI, Webhook

# local imports ----------------------------------------------------------------
from helpers import (read_yaml_data,
                     get_ngrok_url,
                     find_webhook_by_name,
                     delete_webhook, create_webhook)


flask_app = Flask(__name__)
teams_api = None


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
        searchterm = message.text

        # Check message length to avoid array out of bounds
        # if len(searchterm) > 11):
        #     if searchterm[:len("Kalah duck ")] == "Kalah duck ":
        searchterm = searchterm[(len("Kalah duck ")-1):]
        answer = query(searchterm)
        teams_api.messages.create(room.id, text=answer.abstract)
        # else: 
        #     teams_api.messages.create(room.id, text="Search term too short that's what she said.")

        #
        # if message.personId == me.id:
        #     return 'OK'
        # else:
        #     teams_api.messages.create(room.id, text=searchterm +str(email))
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
