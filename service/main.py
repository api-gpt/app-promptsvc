# CS467 Online Capstone: GPT API Challenge
# Kongkom Hiranpradit, Connor Flattum, Nathan Swaim, Noah Zajicek

from flask import Flask, request, session
from flask_session import Session
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os
# from flask import jsonify, send_file
# import requests
import json
# import io

# from pytest import Session
from promptType import promptType
from prompt import prompt

# Load ENV variables
load_dotenv(find_dotenv(".env"))

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

# Set up Flask app
app = Flask(__name__)

# Load configurations from config.py file
# app.config.from_object('config.DevelopmentConfig')

# Configer Flask session variables
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

ERROR_MESSAGE_400 = {
    "svc": "prompt-svc",
    "Error": "The request body is invalid"
    }

# Message log for this session, stores all messages between GPT and user
# an array of 'message' objects
# 'message' objects is a dictionary of "role" and "content"
session_messages = []

###########################################################
#
#  Endpoint to check if prompt-svc is running
#
###########################################################


@app.route('/')
def index():
    return {
        "svc": "prompt-svc",
        "msg": "prompt service is up and running!"
    }

###########################################################
#
#  Route to use prompts with chatGPT API
#
#  Receives:
#   - history:  a history of the conversation
#   - text:     the text of the question to ask
#
#  Returns:
#   - history:  a history of the conversation
#   - text:     the text of the question to ask
#   - answer:   answer to the question prompted
#
###########################################################


@app.route('/v1/prompt/initial-trip-planning-req', methods=['POST'])
def initialRequest():

    content = request.get_json()

    # print(content)
    # check that the request body is valid
    if ('destination' not in content or 'num-users' not in content or
            'num-days' not in content or 'preferences' not in content or 
            'budget' not in content):
        return (ERROR_MESSAGE_400, 400)

    # extract variables from the request body content
    destination = content['destination']
    travelers_num = content['num-users']
    days_num = content['num-days']
    travel_preferences = content['preferences']
    budget = content['budget']


    # create a session variable that stores all message logs
    # the message log is an array of 'message' objects
    # a 'message' objects is a dictionary of "role" and "content"
    completion = None
    session['messages'] = None
    try:
        p = prompt.Prompt()
        session['messages'] = p.initialPlanATrip(destination, travelers_num,
                                                 days_num, travel_preferences,
                                                 budget)
        completion = p.prompt(promptType.PromptType.ChatCompletions,
                              session['messages'])
        print(completion)

    except TypeError:
        return {
            "svc": "prompt-svc",
            "msg": "Invalid type: please use 1) chat,\
                2) embedded, or 3) image",
            "messages": session['messages'],
        }

    # check that the request body is valid
    if ('error' in completion):
        return {
            "svc": "prompt-svc",
            "error": completion['error'],
            "messages": session['messages'],
        }

    # manually add GPT's reply message to message log
    new_message_object = {
            "role": completion.choices[0].message.role,
            "content": [
                {
                    "type": "text",
                    "text": completion.choices[0].message.content
                }
            ]
        }

    session['messages'].append(new_message_object)

    # print(completion)

    return ({"gpt-message": completion.choices[0].message.content}, 200)

###########################################################
#
#  Route to use prompts with chatGPT API
#
#  Receives:
#   - history:  a history of the conversation
#   - text:     the text of the question to ask
#
#  Returns:
#   - history:  a history of the conversation
#   - text:     the text of the question to ask
#   - answer:   answer to the question prompted
#
###########################################################


@app.route('/v1/prompt/itinerary', methods=['POST'])
def chatPrompt():

    # print(request.get_data())

    # get json body from POST request
    content = request.get_json()

    # check that the request body is valid
    if ('messages' not in content):
        return (ERROR_MESSAGE_400, 400)

    try:
        p = prompt.Prompt()
        completion = p.prompt(promptType.PromptType.ChatCompletions,
                              content['messages'])

    except TypeError:
        return {
            "svc": "prompt-svc",
            "error": "Invalid type: please use 1) chat,\
                2) embedded, or 3) image",
            "messages": content['messages'],
        }

    # check that the request body is valid
    if ('error' in completion):
        return {
            "svc": "prompt-svc",
            "error": completion['error'],
            "messages": content['messages'],
        }

    # manually add GPT's reply message to message log
    new_message_object = {
            "role": completion.choices[0].message.role,
            "content": [
                {
                    "type": "text",
                    "text": completion.choices[0].message.content
                }
            ]
        }
    content['messages'].append(new_message_object)

    return {
        "svc": "prompt-svc",
        "messages": content['messages'],
    }


@app.route('/v1/prompt/weather', methods=['POST'])
def weatherPrompt():
    # get json body from POST request
    content = request.get_json()

    # check that the request body is valid
    if ('location' not in content):
        return (ERROR_MESSAGE_400, 400)

    content['messages'] = None
    completion = None

    try:
        p = prompt.Prompt()
        content['messages'] = p.getHourlyForcast(content['location'], 24)
        completion = p.prompt(promptType.PromptType.ChatCompletions,
                              content['messages'])

    except TypeError:
        return {
            "svc": "prompt-svc",
            "msg": "Invalid type: please use 1) chat,\
                2) embedded, or 3) image",
            "messages": content['messages'],
        }

    # check that the request body is valid
    if ('error' in completion):
        return {
            "svc": "prompt-svc",
            "error": completion['error'],
            "messages": content['messages'],
        }

    # print(json.loads(completion.choices[0].message.content))

    # manually add GPT's reply message to message log
    new_message_object = {
            "role": completion.choices[0].message.role,
            "content": [
                {
                    "type": "text",
                    "json": json.loads(completion.choices[0].message.content)
                }
            ]
        }
    
    print('weather update')
    print(content['messages'])

    content['messages'].append(new_message_object)

    # return {
    #     "svc": "prompt-svc",
    #     "messages": content['messages'],
    # }

    return ({"weather-update": completion.choices[0].message.content}, 200)



@app.route('/v1/prompt/trip-planning-chat', methods=['POST'])
def chatTripPlanningPrompt():

    print(request.get_data())

    # get json body from POST request
    content = request.get_json()
    print(content)

    # check that the request body is valid
    if ('message' not in content):
        return (ERROR_MESSAGE_400, 400)

    try:
        p = prompt.Prompt()
        user_message = {
            "role": "user",
            "content": content['message']
        }
        messages = [user_message]
        completion = p.prompt(promptType.PromptType.ChatCompletions, messages)

    except TypeError:
        return {
            "svc": "prompt-svc",
            "error": "Invalid type: please use 1) chat,\
                2) embedded, or 3) image",
            "messages": content['message'],
        }

    # check that the request body is valid
    if ('error' in completion):
        return {
            "svc": "prompt-svc",
            "error": completion['error'],
            "messages": content['message'],
        }

    return ({"messages": completion.choices[0].message.content}, 200)


if __name__ == "__main__":
    app.run()

# Resources used:
#   - https://medium.com/@abed63/flask-application-with-openai-
#     chatgpt-integration-tutorial-958588ac6bdf
#   - https://medium.com/@jcrsch/openai-assistant-with-flask-
#     a-simple-example-with-code-d007ac42ced2
#
