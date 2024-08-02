# CS467 Online Capstone: GPT API Challenge
# Kongkom Hiranpradit, Connor Flattum, Nathan Swaim, Noah Zajicek

from .promptType import PromptType
from .client import Client

# The initial prompt context message for chatGPT to know how to answer
PROMPT_ITINERARY = """You are a professional vacation planner helping users
                    plan trips abroad. You will recommend hotels,
                    attractions, restaurants, shopping area, natural sites
                    or any other places that the user requests. You will
                    plan according to the budget and vacation length given
                    by the user. You will present the result in a format of
                    detailed itinerary of each day, begin from day 1 to the
                    last day."""

PROMPT_WEATHER = """You are a weather service."""

WEATHER_JSON = {
    "time": "string",
    "temperature": "number",
    "condition": "string",
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
            # Make call to chat GPT API
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=1,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            print(completion)
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
                         travel_preferences):

        userText = self.planATripMessage(destination, travelers_num,
                                         days_num, travel_preferences)

        return self.messageConstructor(cleanString(PROMPT_ITINERARY),
                                       userText)

    # Constructs the initial plan a trip message
    def planATripMessage(self, destination, travelers_num, days_num,
                         travel_preferences):

        message = f"""Plan me a {days_num} days trip to {destination}.
                This is for a party of {travelers_num} adults aging
                from 35-38. We are interested in visiting shopping
                area, enjoying local food, with a one or two night
                life. We will strictly stay in Tokyo. Budget should
                be $1500 per person without airfare, but include
                ehotels, meals and other xpenses. We will be
                leaving from New York, USA. {travel_preferences}"""

        return cleanString(message)  # removes whitespace from indendation

    # Gets hourly forcast for the next day at the given location
    def getHourlyForcast(self, location, periods=24):

        forcastMessage = f"""give me an hourly forcast for weather in
                      {location} for the next {periods} hours in
                      json format with this schema: {WEATHER_JSON}"""

        return self.messageConstructor(cleanString(PROMPT_WEATHER),
                                       cleanString(forcastMessage))

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
