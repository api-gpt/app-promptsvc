# CS467 Online Capstone: GPT API Challenge
# Kongkom Hiranpradit, Connor Flattum, Nathan Swaim, Noah Zajicek

from flask import Flask, request
from flask_session import Session
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os
# from flask import jsonify, send_file
# import requests
import json
# import io

# from pytest import Session
from service.promptType import promptType
from service.prompt import prompt
from service.postgres.postgresdb import PostgresDB

# Load ENV variables
load_dotenv(find_dotenv(".env"))

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

# Set up Flask app
app = Flask(__name__)

# Load configurations from config.py file
# app.config.from_object('service.config.DevelopmentConfig')

# Configer Flask session variables
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

ERROR_MESSAGE_400 = {
    "svc": "prompt-svc",
    "Error": "The request body is invalid"
}

# constants to define messages data in Postgres's messages table
SYSTEMPROMPT = "SYSTEMPROMPT"   # System Prompt first sent to GPT
USERPROMPT = "USERPROMPT"       # User Prompt first sent to GPT
USERCHAT = "USERCHAT"           # any chat from user after the initial prompts
GPTCHAT = "GPTCHAT"             # any reply from GPT other than Itinerary
ITINERARY = "ITINERARY"         # reply from GPT that is an Itinerary

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
#  1. Initial itenerary request. Routed from UI's "Get Itinerary" button
#
#  Receives:
#   - POST JSON content from form:
#       {destination, num-users, num-days, preferences, budget}
#   - Create a new trip in database
#   - Stores system prompt, user prompt and GPT response in database
#
#  Returns:
#   - JSON: {"gpt-message": GPT's response in Itinerary format [library],
#            "trip_id": Database's trip ID for future references [int]}
#
###########################################################
@app.route('/v1/prompt/initial-trip-planning-req', methods=['POST'])
def initialRequest():

    content = request.get_json()

    # print(content)
    # check that the request body is valid
    if ('destination' not in content or 'num-users' not in content or
            'num-days' not in content or 'preferences' not in content or
            'budget' not in content or 'user_id' not in content):
        return (ERROR_MESSAGE_400, 400)

    # extract variables from the request body content
    destination = content['destination']
    travelers_num = content['num-users']
    days_num = content['num-days']
    travel_preferences = content['preferences']
    budget = content['budget']
    user_id = content['user_id']

    # messages is an array of 'message' objects
    # a 'message' objects is a dictionary of "role" and "content"
    completion = None
    messages = None
    try:
        print("Initial req: constructing system message and sending to GPT")
        p = prompt.Prompt()
        messages = p.initialPlanATrip(destination, travelers_num,
                                      days_num, travel_preferences,
                                      budget)
        completion = p.prompt(promptType.PromptType.ChatCompletions,
                              messages)
        print("Initial req: succesfully recieved completion from GPT")
        # print(completion)

    except TypeError:
        return {
            "svc": "prompt-svc",
            "msg": "Invalid type: please use 1) chat,\
                2) embedded, or 3) image",
            "messages": messages,
        }

    # check that the request body is valid
    if ('error' in completion):
        return {
            "svc": "prompt-svc",
            "error": completion['error'],
            "messages": messages,
        }

    # Database work (no need for try blocks, they are already in postgresdb.py)
    # create a PostgresDB() object, this automatically connects to PostgresDB
    postgressconn = PostgresDB()

    # create a new trip on the db's 'trips' table, return auto-gen trip_id
    trip_id = postgressconn.create_trip_to_db(
                                destination=destination,
                                days_num=days_num,
                                travelers_num=travelers_num,
                                budget=budget,
                                travel_preferences=travel_preferences,
                                user_id=user_id)

    # create a new system prompt on db's 'messages' table
    postgressconn.create_message_to_db(trip_id=trip_id,
                                       role=messages[0]['role'],
                                       content_type=messages[0]['content'][0]['type'],
                                       content_text=messages[0]['content'][0]['text'],
                                       message_category=SYSTEMPROMPT)

    # create a new user prompt on db's 'messages' table
    postgressconn.create_message_to_db(trip_id=trip_id,
                                       role=messages[1]['role'],
                                       content_type=messages[1]['content'][0]['type'],
                                       content_text=messages[1]['content'][0]['text'],
                                       message_category=USERPROMPT)

    # create a new GPT's reply message to 'messages' table
    postgressconn.create_message_to_db(trip_id=trip_id,
                                       role=completion.choices[0].message.role,
                                       content_type="text",
                                       content_text=completion.choices[0].message.content,
                                       message_category=ITINERARY)

    # close postgres DB connection
    postgressconn.close_db_connection()

    return ({"gpt-message": completion.choices[0].message.content,
             "trip_id": trip_id}, 200)


###########################################################
#
#  2. Get trip from trip_id. Can access from URL
#
#  Receives:
#   - URL variable: trip_id
#   - Search for the most recent updated itinerary
#
#  Returns:
#   - JSON: {"gpt-message": most recent updated itinerary [library],
#            "trip_id": Database's trip ID for future references [int]}
#
###########################################################
@app.route('/v1/prompt/get-trip/<trip_id>', methods=['GET'])
def getTrip(trip_id):

    # Extract user_id from header
    if 'Authorization' in request.headers:
        # remove the word "Bearer" from the header: Authorization string
        header = request.headers['Authorization'].split()
        user_id = header[1]
    else:
        user_id = None

    print(f"Get trip: user_id = {user_id}")

    # Database work (no need for try blocks, they are already in postgresdb.py)
    # create a PostgresDB() object, this automatically connects to PostgresDB
    postgressconn = PostgresDB()

    # get trip from database
    trip = postgressconn.get_trip(trip_id)

    # get most recent itinerary from database
    recent_itinerary = postgressconn.get_recent_itinerary(trip_id)

    # close postgres DB connection
    postgressconn.close_db_connection()

    # check that the correct user is requesting the trip
    if (user_id == trip['user_id']):
        return ({"gpt-message": recent_itinerary,
                 "trip_id": trip_id,
                 "destination": trip['destination']}, 200)
    else:
        return ({"Error": "Unauthorized, this trip does not belong to you."},
                401)


@app.route('/v1/prompt/get-trip-history', methods=['GET'])
def getHistory():

    # Extract user_id from header
    if 'Authorization' in request.headers:
        # remove the word "Bearer" from the header: Authorization string
        header = request.headers['Authorization'].split()
        user_id = header[1]
    else:
        # if there's no auth header, raise error
        raise Exception({"code": "no auth header",
                         "description": "Authorization header is missing"}, 
                        401)

    # Database work (no need for try blocks, they are already in postgresdb.py)
    # create a PostgresDB() object, this automatically connects to PostgresDB
    postgressconn = PostgresDB()

    # get all trips of a user and store in 'history'
    history = postgressconn.get_trip_from_user(user_id)

    # close postgres DB connection
    postgressconn.close_db_connection()

    return ({"history": history}, 200)


###########################################################
#
#  3. Route to use prompts with chatGPT API
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


###########################################################
#
#  4. Route to use prompts with chatGPT API
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
@app.route('/v1/localInfo', methods=['POST'])
def localInfo():

    # print(request.get_data())

    content = request.get_json()

    # print(content)
    # check that the request body is valid
    if ('destination' not in content or
            'time' not in content or
            'date' not in content or
            'resterauntConditions' not in content):
        return (ERROR_MESSAGE_400, 400)

    # extract variables from the request body content
    destination = content['destination']
    time = content['time']
    date = content['date']
    resterauntConditions = content['resterauntConditions']

    try:
        p = prompt.Prompt()
        # Create prompt message for local info
        content['messages'] = p.getLocalInfo(destination, time,
                                             date, resterauntConditions)
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


###########################################################
#
#  5. Weather Prompt
#
#  Receives:
#
#  Returns:
#
#
###########################################################
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
        content['messages'] = p.getHourlyForcast(content['location'])
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
    # print(content['messages'])

    content['messages'].append(new_message_object)

    # return {
    #     "svc": "prompt-svc",
    #     "messages": content['messages'],
    # }

    return ({"weather-update": completion.choices[0].message.content}, 200)


###########################################################
#
#  6. User chat with GPT, from UI's chat-box "Send"
#   This doesn't update the itinerary, just basic chatting.
#
#  Receives:
#   - POST JSON content from form:
#       {trip_id, message}
#   - Looks up chat history of trip by trip_id
#   - Stores new user prompt and GPT response in database
#
#  Returns:
#   - JSON: {"messages": GPT's response in normal format [string]}
#
###########################################################
@app.route('/v1/prompt/trip-planning-chat', methods=['POST'])
def chatTripPlanningPrompt():

    print(request.get_data())

    # get json body from POST request
    content = request.get_json()
    trip_id = content['trip_id']
    user_chat_message = content['message']

    # check that the request body is valid
    if ('message' not in content or 'trip_id' not in content):
        return (ERROR_MESSAGE_400, 400)

    # read chat history from database using trip_id
    # Database work (no need for try blocks, they are already in postgresdb.py)
    # create a PostgresDB() object, this automatically connects to PostgresDB
    postgressconn = PostgresDB()

    # read all messages with trip_id from 'message' table in database
    # returns an array of message objects
    messages = postgressconn.get_chat_history(trip_id)
    print("User chat: retrieved chat history from database")

    try:
        p = prompt.Prompt()
        user_message = {
            "role": "user",
            "content": [{
                "type": "text",
                "text": user_chat_message + " Answer in normal formatting."
            }]
        }
        messages.append(user_message)
        completion = p.prompt(promptType.PromptType.ChatCompletions, messages)

    except TypeError:
        return {
            "svc": "prompt-svc",
            "error": "Invalid type: please use 1) chat,\
                2) embedded, or 3) image",
            "messages": user_chat_message,
        }

    # check that the request body is valid
    if ('error' in completion):
        return {
            "svc": "prompt-svc",
            "error": completion['error'],
            "messages": user_chat_message,
        }

    # create a new user prompt on db's 'messages' table
    postgressconn.create_message_to_db(trip_id=trip_id,
                                       role="user",
                                       content_type="text",
                                       content_text=user_chat_message,
                                       message_category=USERCHAT)

    # create a new GPT's reply message to 'messages' table
    postgressconn.create_message_to_db(trip_id=trip_id,
                                       role=completion.choices[0].message.role,
                                       content_type="text",
                                       content_text=completion.choices[0].message.content,
                                       message_category=GPTCHAT)

    # close postgres DB connection
    postgressconn.close_db_connection()

    return ({"messages": completion.choices[0].message.content}, 200)


###########################################################
#
#  7. User Updates the itinerary after chatting with GPT
#   This gathers all alteration the user requested and asks GPT to revise
#
#  Receives:
#   - HTTP POST JSON content: {trip_id}
#   - Looks up chat history of trip by trip_id
#   - Send pre-generated prompt to GPT to revise itinerary
#
#  Returns:
#   - JSON: {"gpt-message": GPT's response in Itinerary format [library],
#            "trip_id": Database's trip ID for future references [int]}
#
###########################################################
@app.route('/v1/prompt/trip-planning-update', methods=['POST'])
def updateTripPlanningPrompt():

    print(request.get_data())

    # get json body from POST request
    content = request.get_json()

    # check that the request body is valid
    if ('trip_id' not in content):
        return (ERROR_MESSAGE_400, 400)

    trip_id = content['trip_id']

    # read chat history from database using trip_id
    # Database work (no need for try blocks, they are already in postgresdb.py)
    # create a PostgresDB() object, this automatically connects to PostgresDB
    postgressconn = PostgresDB()

    # read all messages with trip_id from 'message' table in database
    # returns an array of message objects
    messages = postgressconn.get_chat_history(trip_id)
    print("Update itinerary: retrieved chat history from database")

    try:
        p = prompt.Prompt()
        user_message = {
            "role": "user",
            "content": [{
                "type": "text",
                "text": p.updateATripMessage()
            }]
        }
        messages.append(user_message)
        completion = p.prompt(promptType.PromptType.ChatCompletions, messages)
        print("Update itinerary: succesfully recieved completion from GPT")

    except TypeError:
        return {
            "svc": "prompt-svc",
            "error": "Invalid type: please use 1) chat,\
                2) embedded, or 3) image",
            "messages": p.updateATripMessage,
        }

    # check that the request body is valid
    if ('error' in completion):
        return {
            "svc": "prompt-svc",
            "error": completion['error'],
            "messages": p.updateATripMessage,
        }

    # create a new user prompt on db's 'messages' table
    postgressconn.create_message_to_db(trip_id=trip_id,
                                       role="user",
                                       content_type="text",
                                       content_text=p.updateATripMessage(),
                                       message_category=USERCHAT)

    # create a new GPT's reply message to 'messages' table
    postgressconn.create_message_to_db(trip_id=trip_id,
                                       role=completion.choices[0].message.role,
                                       content_type="text",
                                       content_text=completion.choices[0].message.content,
                                       message_category=ITINERARY)

    # get location from trips table for the weather service
    trip = postgressconn.get_trip(trip_id=trip_id)
    destination = trip['destination']

    # close postgres DB connection
    postgressconn.close_db_connection()

    return ({"gpt-message": completion.choices[0].message.content,
             "destination": destination}, 200)


@app.route('/v1/prompt/profile', methods=['GET'])
def getUserProfile():

    # Extract user_id from header
    if 'Authorization' in request.headers:
        # remove the word "Bearer" from the header: Authorization string
        header = request.headers['Authorization'].split()
        user_id = header[1]
    else:
        return {
            "error": "Unauthorized access forbidden"
        }

    # Database work (no need for try blocks, they are already in postgresdb.py)
    # create a PostgresDB() object, this automatically connects to PostgresDB
    postgressconn = PostgresDB()

    profile = postgressconn.get_profile(user_id)

    if profile is None:
        return {
            "error": "Error with database"
        }

    return profile


@app.route('/v1/prompt/profile', methods=['POST'])
def updateUserProfile():

    print("updating user profile")

    # Extract user_id from header
    if 'Authorization' in request.headers:
        # remove the word "Bearer" from the header: Authorization string
        header = request.headers['Authorization'].split()
        user_id = header[1]
    else:
        print("unauthorized")
        return {
            "error": "Unauthorized access forbidden"
        }

    # get json body from POST request
    content = request.get_json()
    print(content)

    # check that the request body is valid
    if ('age' not in content or
            'travelStyle' not in content or
            'travelPriorities' not in content or
            'travelAvoidances' not in content or
            'dietaryRestrictions' not in content or
            'accomodations' not in content):
        return (ERROR_MESSAGE_400, 400)

    # Get form data
    age = content['age']
    travelStyle = content['travel-style']
    travelPriorities = content['travel-priorities']
    travelAvoidances = content['travel-avoidances']
    dietaryRestrictions = content['dietary-restrictions']
    accomodations = content['accomodations']

    # Database work (no need for try blocks, they are already in postgresdb.py)
    # create a PostgresDB() object, this automatically connects to PostgresDB
    postgressconn = PostgresDB()

    profile = postgressconn.get_profile(user_id)
    response = None

    if profile is not None:
        response = postgressconn.update_profile(age, travelStyle,
                                                travelPriorities,
                                                travelAvoidances,
                                                dietaryRestrictions,
                                                accomodations, user_id)
    else:
        response = postgressconn.insert_profile(user_id, age, travelStyle,
                                                travelPriorities,
                                                travelAvoidances,
                                                dietaryRestrictions,
                                                accomodations)

    if response is None:
        return {
            "error": "Error with database"
        }

    return {
        "msg": response
    }


if __name__ == "__main__":
    app.run()

# Resources used:
#   - https://medium.com/@abed63/flask-application-with-openai-
#     chatgpt-integration-tutorial-958588ac6bdf
#   - https://medium.com/@jcrsch/openai-assistant-with-flask-
#     a-simple-example-with-code-d007ac42ced2
#
