from flask import Flask, request, session
from flask_session import Session
from app.web.oauth import oauth, oauth_bp
from openai import OpenAI
from dotenv import load_dotenv
# from flask import jsonify, send_file
import os
# import requests
# import json
# import io

# Create Flask application
app = Flask(__name__)

# Load configurations from config.py file
app.config.from_object('app.web.config.DevelopmentConfig')

# Configer Flask session variables
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

load_dotenv()
# This line brings all environment variables from .env into os.environ
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=OPENAI_API_KEY)
# defaults to getting the key using os.environ.get("OPENAI_API_KEY")
# if you saved the key under a different environment variable name,
# you can do something like:
# client = OpenAI(
#   api_key=os.environ.get("CUSTOM_ENV_NAME"),
# )

# Initialize OAuth with the created Flask app
oauth.init_app(app)

# Register OAuth blueprint
app.register_blueprint(oauth_bp)

ERROR_MESSAGE_400 = {"Error": "The request body is invalid"}

# Message log for this session, stores all messages between GPT and user
# an array of 'message' objects
# 'message' objects is a dictionary of "role" and "content"
session_messages = []


# just for testing GPT API with a fixed message
# returns GPT's completing message string
@app.route('/', methods=['GET'])
def home():
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": ("You are a poetic assistant, skilled in "
                            "explaining complex programming concepts "
                            "with creative flair.")
                },
            {
                "role": "user",
                "content": ("Compose a poem that explains the concept of "
                            "recursion in programming.")
                }
        ]
    )

    return completion.choices[0].message.content


# initial trip request to GPT
# request body must include 'destination', 'travelers_num', 'days_num'
#   and 'travel_preference'
# returns GPT's completion message string
@app.route('/gpt', methods=['POST'])
def initial_gpt_chat():
    # get json body from POST request
    content = request.get_json()
    # check that the request body is valid
    if ('destination' not in content or 'travelers_num' not in content or
            'days_num' not in content or 'travel_preference' not in content):
        return (ERROR_MESSAGE_400, 400)

    # extract variables from the request body content
    destination = content['destination']
    travelers_num = content['travelers_num']
    days_num = content['days_num']
    travel_preference = content['travel_preference']

    # create a session variable that stores all message logs
    # the message log is an array of 'message' objects
    # a 'message' objects is a dictionary of "role" and "content"
    session['messages'] = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "You are a professional vacation planner helping "
                        "users plan trips abroad. You will recommend hotels, "
                        "attractions, restaurants, shopping area, natural "
                        "sites or any other places that the user requests. "
                        "You will plan according to the budget and vacation "
                        "length given by the user. You will present the "
                        "result in a format of detailed itinerary of each "
                        "day, begin from day 1 to the last day."
                    )
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Plan me a {days_num} days trip to {destination}. "
                        f"This is for a party of {travelers_num} adults aging "
                        f"from 35-38. We are interested in visiting shopping "
                        f"area, enjoying local food, with a one or two night "
                        f"life. We will strictly stay in Tokyo. Budget should "
                        f"be $1500 per person without airfare, but include "
                        f"ehotels, meals and other xpenses. We will be "
                        f"leaving from New York, USA. {travel_preference}"
                    )
                }
            ]
        }
    ]

    # call on GPT API with the message log
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=session['messages'],
        temperature=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

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

    return completion.choices[0].message.content


# user's message to GPT after the initial request
# request body must include 'user_message'
# returns GPT's completion message string
@app.route('/gpt', methods=['PATCH'])
def user_gpt_chat():
    # get json body from POST request
    content = request.get_json()
    # check that the request body is valid
    if ('user_message' not in content):
        return (ERROR_MESSAGE_400, 400)

    # extract variables from the request body content
    new_message_object = {
        "role": "user",
        "content": [
                {
                    "type": "text",
                    "text": content['user_message']
                }
            ]
    }

    # add user's message to the message log session variable
    session['messages'].append(new_message_object)

    # call on GPT API with the message log
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=session['messages'],
        temperature=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

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

    return completion.choices[0].message.content


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
