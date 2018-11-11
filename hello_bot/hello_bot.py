#!/usr/bin/env python
#  -*- coding: utf-8 -*-

# 3rd party imports ------------------------------------------------------------
from flask import Flask, request
from webexteamssdk import WebexTeamsAPI, Webhook
import nltk
import json
import time
import random, requests

from thesaurus import Word
from textblob import TextBlob
from duckduckpy import query
from search_news import search_news
from twilio_sendMsg import send_text_message
from twilio_makeCall import send_voice_msg

COMPANY_NAME = "Barclays"
TEAM_NAME = "Integration"
PRODUCT_NAME1 = "Barclaycard"
PRODCUT_NAME2 = "Barclays Account"

#nltk.download('punkt')
#nltk.download('wordnet')

jayc = '+447731981339'
js = '+447874170099'
firdaus = '+447476464666'
shash = '+447341052333'

number_list = [jayc, js, firdaus, shash]
person_names = ['jayc', 'js', 'firdaus', 'shash']

person_dict = {
    'jayc': '+447731981339',
    'js': '+447874170099',
    'firdaus': '+447476464666',
    'shash': '+447341052333'
}

# local imports ----------------------------------------------------------------
from helpers import (read_yaml_data,
                     get_ngrok_url,
                     find_webhook_by_name,
                     delete_webhook, create_webhook)


flask_app = Flask(__name__)
teams_api = None

greeting_tokens = ["hello", "hi", "heya", "hiya", "hie", "wassup", ]
rec_tokens =  ["rec", "recording"]
start_token = ["start"]
stop_token = ["stop"]
search_token = ["search", "Search"]
news_token = ["news", "articles", "newspaper"]
msg_tokens = ["msg", "message", "sms"]
voice_token = ["voice"]
quote_token = ["quotes", "quote"]
synonym_token = ["synonyms", "synonym"]
antonym_token = ["antonyms", "antonym"]
origin_token = ["origins", "origin"]
examples_token = ["ex", "examples", "example", "eg"]
into_token = ["can", "you", "do", "help"]
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
            response, polarity_report, subjectivity_report, return_result, thes_words = generate_response(message, room.id)
            teams_api.messages.create(room.id, text=response)
            time.sleep(3)
            for key in polarity_report:
                if (key == "overall"):
                    teams_api.messages.create(room.id, text="the overall chat was " + polarity_report[key])
                else:
                    teams_api.messages.create(room.id, text="user " + key + " was " + polarity_report[key])
            if (return_result == ""):
                pass
            else:
                if return_result[0] == 0:
                    teams_api.messages.create(room.id, text=str(return_result[1]))
                else:
                    for i in range(len(return_result[1])):
                        # print(len(return_result[1]))
                        teams_api.messages.create(room.id, text=str(return_result[1][i]))
            if (thes_words == ""):
                pass
            else:
                for x in thes_words:
                    teams_api.messages.create(room.id, text=x)
            return 'OK'
    else:
        print('received none post request, not handled!')

def generate_response(message, roomid):
    response = ""
    polarity_report = ""
    subjectivity_report = ""
    return_result = ""
    thes_words = ""
    user_input = message.text
    user_input = user_input.lower()
    word_tokens = nltk.word_tokenize(user_input)
    compGreet = set(word_tokens) & set(greeting_tokens)
    #print (word_tokens)
    compRec = set(word_tokens) & set (rec_tokens)
    compSearch = set(word_tokens) & set(search_token)
    compMsg = set(word_tokens) & set(msg_tokens)
    compQuote = set(word_tokens) & set(quote_token)
    compSyn = set(word_tokens) & set(synonym_token)
    compAnt = set(word_tokens) & set(antonym_token)
    compOrig = set(word_tokens) & set(origin_token)
    compEx = set(word_tokens) & set(examples_token)
    compIn = set(word_tokens) & set(into_token)
    if (compSyn):
        index1 = word_tokens.index('of')
        word = word_tokens[index1 + 1:index1 +2]
        word = ' '.join(word)
        word = word.strip()
        w = Word(word)
        if len(w.synonyms()) == 0:
            response = "sorry, there are no synonyms for word " + word
        else:
            response = "The synonyms are"
            thes_words = w.synonyms().copy()
            thes_words = thes_words[:3]
    elif (compAnt):
        index1 = word_tokens.index('of')
        word = word_tokens[index1 + 1:index1 +2]
        word = ' '.join(word)
        word = word.strip()
        w = Word(word)
        if len(w.antonyms()) == 0:
            response = "sorry, there are no antonyms for word " + word
        else:
            response = "The antonyms are"
            thes_words = w.antonyms().copy()
            thes_words = thes_words[:3]
    elif (compEx):
        index1 = word_tokens.index('of')
        word = word_tokens[index1 + 1:index1 +2]
        word = ' '.join(word)
        word = word.strip()
        w = Word(word)
        if len(w.examples()) == 0:
            response = "sorry, there are no examples for word " + word
        else:
            response = "The examples are"
            thes_words = w.examples().copy()
            thes_words = thes_words[:3]
    elif (compOrig):
        index1 = word_tokens.index('of')
        word = word_tokens[index1 + 1:index1 +2]
        word = ' '.join(word)
        word = word.strip()
        w = Word(word)
        orig = w.origin()
        if(orig == ""):
            response = "Cannot find origin of " + word
        else:
            response = "The origin is : - "
            thes_words = orig
    elif (compQuote):
        url = "https://www.forbes.com/forbesapi/thought/uri.json?enrich=true&query=1&relatedlimit=200"
        response = requests.get(url)
        data = response.json()
        rng = random.random()*140
        quote = data['thought']['relatedThemeThoughts'][round(rng)]["quote"]
        author = data['thought']['relatedThemeThoughts'][round(rng)]["thoughtAuthor"]["name"]
        response = quote + ' - ' +author
    elif (compMsg):
        if (set(word_tokens) & set(voice_token)):
            #VOICEMSG
            index1 = word_tokens.index('to')
            contactPerson = word_tokens[index1 + 1:]
            contactPerson = ' '.join(contactPerson)
            contactPerson = contactPerson.strip()
            send_voice_msg(contactPerson, person_dict.get(contactPerson))
            response = "Nice! message sent to " + contactPerson
        else:
            index1 = word_tokens.index('to')
            index2 = word_tokens.index('-')
            contactPerson = word_tokens[index1 + 1:index2]
            contactPerson = ' '.join(contactPerson)
            contactPerson = contactPerson.strip()
            msg = word_tokens[index2 + 1:]
            msg = ' '.join(msg)
            send_text_message(contactPerson, person_dict.get(contactPerson), msg)
            response = "Nice! message sent to " + contactPerson
    elif (compRec):
        if (set(word_tokens) & set (start_token)):
            response = "Ok Starting chat recording ////"
        elif (set(word_tokens) & set (stop_token)):
            response = "Ok Stoping chat recording \/\/\/"
            polarity_report, subjectivity_report = sentiment_analysis(message.id, roomid)
        else:
            response = "Please mention to start or stop recording"
    elif (compSearch):
        if (set(word_tokens) & set(news_token)):
            if (set(word_tokens) & set(['-'])):
                index = index = word_tokens.index('-')
                searchtermlist = word_tokens[index + 1:]
                searchterm = ' '.join(searchtermlist)
                searchterm = searchterm.strip()
            else:
                searchterm = COMPANY_NAME
            print(searchterm)
            return_result = search_news(searchterm)
            response = "Here are the search results: - "
        else:
            index = word_tokens.index('-')
            searchtermlist = word_tokens[index + 1:]
            searchterm = ' '.join(searchtermlist)
            searchterm = searchterm.strip()
            print(searchterm)
            answer = query(searchterm)
            print(answer.type)
            if (answer.abstract == ""):
                pass
            else:
                response="Here is your search result /n" + answer.abstract
    elif (compGreet):
        response = "Hello fellow member, how can I help you?" #/n Here are some services I provide : - /n
    elif (compIn):
        response =" Here are a few services I provide \n \
        - I can check synonyms, antonyms and examples of a word for you \n \
        - I can also record meeting that is presented through the platform and do sentimental analysis on the conversation \n \
        - I can also call and text people for you \n \
        - I can also use search engines and find the most recent news for you"
    else:
        response = "Sorry I did not understand you..."
    #for i in word_tokens :
        #print(i)

    #print("response" + response)
    return response, polarity_report, subjectivity_report, return_result, thes_words

def sentiment_analysis(messageId, roomId):
    #data gathering part
    response_data = []
    api = WebexTeamsAPI(access_token = "ZTZkNDlhMDItYmRhNi00NTg4LWIxYmItZGU1ODNlOWQwM2U5MWYwYzhmZGEtOTE5")
    genObj = api.messages.list(roomId,beforeMessage=messageId)
    for x in genObj:
        response_data.append(x)
        if "////" in x.text:
            break

    #for x in response_data:
        #print(x.text)

    userIds = []

    for x in response_data:
        if ((x.personId in userIds)):
            pass
        else:
            userIds.append(x.personId)

    user_texts = {}
    for x in userIds[:]:
        user_texts[x] = []

    for x in response_data:
        user_texts[x.personId].append(x.text)

    for x in userIds:
        user_texts[api.people.get(x).displayName] = user_texts.pop(x)

    sentiment_coll = []
    polarity_report = {}
    subjectivity_report = {}
    convo_sentiment={}
    del user_texts["EasyBot"]
    convo_string = ""
    print("values")
    for key,value in user_texts.items():
        print(key)
        polarity_report[key] = 0
        subjectivity_report[key] = 0
        for i in value:
            convo_string += " " + i + "."
            polarity, subjectivity = blob_helper(i)
            polarity_report[key] += polarity
            subjectivity_report[key] += subjectivity
    print("stop print values")
    polarity, subjectivity = blob_helper(convo_string)
    polarity_report["overall"] = polarity
    subjectivity_report["overall"] = subjectivity
    for x in sentiment_coll[:]:
        print(x)

    print("--------------------")
    print(convo_sentiment)

    chat_polarity = ""

    for key in polarity_report:

        if(polarity_report[key] > 0.5):
            polarity_report[key] = "very positive"
        elif(polarity_report[key] >0):
            polarity_report[key] = "positive"
        elif(polarity_report[key] > -0.5):
            polarity_report[key] = "negative"
        else:
            polarity_report[key] = "very negative"

    return polarity_report, subjectivity_report
    #print(user_texts)

def blob_helper(input):
    blob = TextBlob(input)
    output = blob.sentiment
    polarity = getattr(output, 'polarity')
    subjectivity = getattr(output, 'subjectivity')

    return polarity, subjectivity

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
