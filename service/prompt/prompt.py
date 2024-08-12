# CS467 Online Capstone: GPT API Challenge
# Kongkom Hiranpradit, Connor Flattum, Nathan Swaim, Noah Zajicek

from service.promptType.promptType import PromptType
from service.client.client import Client

# The initial prompt context message for chatGPT to know how to answer
PROMPT_ITINERARY = """You are a professional vacation planner helping users
                    plan trips abroad. You will recommend hotels,
                    attractions, restaurants, shopping area, natural sites
                    or any other places that the user requests. You will
                    plan according to the budget and vacation length given
                    by the user. You will present the result in a format of
                    detailed itinerary of each day, begin from day 1 to the
                    last day."""


ITINERARY_JSON = {
    "time": "string",
    "location": "string",
    "activity": "string",
    "average duration": "number",
    "cost": "number",
    "travel methods": "string",
    "nearby resteraunts": "string",
    "tips": "string",
    "nearby activity": "string"
}

PROMPT_UPDATE = f"""Give me an updated itinerary of everything we discussed up
                    to this point. Use the following json format with this
                    schema: {ITINERARY_JSON} where time is based on 12 hour
                    clock, cost is a dollar amount, and average duration is in
                    hours. It will be housed within this structure
                    " "Day 1": [], "Day 2": [], "Day 3": [] " and so on until
                    the last day."""
                
PROMPT_WEATHER = """You are a weather service."""

WEATHER_JSON = {
    "time": "string",
    "temperature": "number",
    "condition": "string",
    "FahrenheitorCelsius": "string",
    "chance_of_rain": "number"
}


# Prompt class used to make chat GPT prompts
class Prompt():

    def __init__(self) -> None:
        self.client = Client().getClient()

    ###########################################################
    #
    #  Prompts the ChatGPT client based on the prompt type.
    #
    #  Receives:
    #   - promptType:  a PromptType enumeration of the prompt
    #                  type
    #   - options:     options used for the prompt
    #
    #  Returns:
    #   - a response from the ChatGPT client
    #
    #  Throws:
    #   - TypeError:    throws TypeError if prompt type is
    #                    invalid
    #
    ###########################################################
    def prompt(self, promptType, options):
        match(promptType):
            case PromptType.ChatCompletions:
                return self.promptChatCompletions(options)
            case PromptType.Embeddings:
                return self.promptEmbeddings(options)
            case PromptType.Images:
                return self.promptImages(options)
            case _:
                raise TypeError("Invalid Prompt Type: {promptType}")

    # Helper method for Chat GPT chat completion prompts
    def promptChatCompletions(self, messages):

        try:
            # print(messages)
            # Make call to chat GPT API
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=1,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            # print(completion)
            return completion
        except Exception as e:
            print(e)
            return {
                "error": f"Error proocessing request: {e}"
            }

    # Helper method for Chat GPT embedded prompts
    def promptEmbeddings(self, options):
        print(options)
        completion = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=options.get('text')
        )

        return completion.to_json()

    # Helper method for Chat GPT image prompts
    def promptImages(self, options):
        completion = self.client.images.generate(
            prompt=options.get('text'),
            n=2,
            size=options.get('size')
        )

        return completion.to_json()

    # Helper method for intial trip planning message construction
    def initialPlanATrip(self, destination, travelers_num, days_num,
                         travel_preferences, budget):

        userText = self.planATripMessage(destination, travelers_num,
                                         days_num, travel_preferences, budget)

        return self.messageConstructor(cleanString(PROMPT_ITINERARY),
                                       userText)

    # Constructs the initial plan a trip message
    def planATripMessage(self, destination, travelers_num, days_num,
                         travel_preferences, budget):

        message = f"""Plan me a {days_num} days trip to {destination}.
                This is for a party of {travelers_num} adults aging
                from 35-38. We are interested in visiting shopping
                area, enjoying local food, with a one or two night
                life. We will strictly stay in {destination}. Budget should
                be {budget} per person without airfare, but include
                ehotels, meals and other expenses. {travel_preferences}
                Use the following json format with this schema:
                {ITINERARY_JSON}
                where time is based on 12 hour clock, cost is a dollar amount,
                and average duration is in hours. It will be housed within this
                structure " "Day 1": [], "Day 2": [], "Day 3": [] " and so on
                until the last day."""

        return cleanString(message)  # removes whitespace from indendation

    # Constructs an update itinerary message
    def updateATripMessage(self):
        return cleanString(PROMPT_UPDATE)

    # Gets hourly forcast for the next day at the given location
    def getHourlyForcast(self, location):

        forcastMessage = f"""give me an hourly forcast for weather in
                      {location} for the next 24 hours in
                      json format with this schema: {WEATHER_JSON}
                      using a 12 hour clock. The WEATHER_JSON formatted output
                      will be housed within this structure "forecast":[].
                      Weather conditions will be identified as "Clear Night",
                     "Rainy Night", "Cloudy Night", "Sunny", "Partly Cloudy",
                       "Rainy", "Stormy", "Cloudy", or "Snowy"
                       """

        return self.messageConstructor(cleanString(PROMPT_WEATHER),
                                       cleanString(forcastMessage))


    # Constructs the initial plan a trip message
    def respondToTripChat(self, travel_preferences):

        message = f"""Give a response to a customer based on their chat response as they are planning their travel itinerary. 
        Here is their response {travel_preferences}"""

        return cleanString(message)  # removes whitespace from indendation

    def getLocalInfo(self, destination, time, date,
                     resterauntConditions):

        # Create message to get local info for event
        # Weather, resteraunts, and travel options

        localInfoMessage = f"""Give me the weather for {destination} at
                        {time} on {date}. Give me travel options to
                        {destination}. Give me good resteraunts near
                        {destination}. Also, give me alternative things
                        to do around this area. {resterauntConditions}
                        """

        return self.messageConstructor(cleanString(PROMPT_ITINERARY),
                                       cleanString(localInfoMessage))

    # Helper method to construct messages
    def messageConstructor(self, systemText, userText):

        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": systemText
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": userText
                    }
                ]
            }
        ]

        return messages


# Cleans a string of indentation spaces
def cleanString(string):
    return ' '.join(string.split())
