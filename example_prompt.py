# CS467 Online Capstone: GPT API Challenge
# Kongkom Hiranpradit, Connor Flattum, Nathan Swaim, Noah Zajicek
# 14 July 2024

from openai import OpenAI
client = OpenAI()

# Systema and User strings below are hardcoded.
# We can declare variables such as Number_of_days, Party_size,
# Destination, etc.
# Then alter the system or user string by inserting these variables.
# The end user can select these variables via our website UI.

completion = client.chat.completions.create(
  model="gpt-3.5-turbo-0125",
  messages=[
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": (
            "You are a professional vacation planner helping users plan"
            "trips abroad. You will recommend hotels, attractions, "
            "restaurants, shopping area, natural sites or any other places "
            "that the user requests. You will plan according to the budget "
            "and vacation length given by the user. You will present the "
            "result in a format of detailed itinerary of each day, "
            "begin from day 1 to the last day."
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
            "Plan me a 7 days trip to Tokyo, Japan. This is for a party of "
            "4 adults aging from 35-38. We are interested in visiting "
            "shopping area, enjoying local food, with a one or two night "
            "life. We will strictly stay in Tokyo. Budget should be $1500 "
            "per person without airfare, but include hotels, meals and other "
            "expenses. We will be leaving from New York, USA."
          )
        }
      ]
    }
  ],
  temperature=1,
  max_tokens=256,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)

print(completion.choices[0].message)
# or directly access content with <completion.choices[0].message.content>
