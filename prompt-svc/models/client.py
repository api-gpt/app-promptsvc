# CS467 Online Capstone: GPT API Challenge
# Kongkom Hiranpradit, Connor Flattum, Nathan Swaim, Noah Zajicek

from openai import OpenAI
import os


# Client class creates a chatGPT client using the environment API key
class Client():

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            organization=None,
            project=None,
            base_url=None,
            timeout=None,
            max_retries=0,
            default_headers=None,
            default_query=None,
            http_client=None,
        )

    # Returns the chat GPT client
    def getClient(self) -> OpenAI:
        return self.client