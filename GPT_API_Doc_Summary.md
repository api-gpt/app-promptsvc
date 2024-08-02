# GPT API DOCUMENTATION SUMMARY AND TAKEAWAYS
_Source: https://platform.openai.com/docs_
## Current Available GPT Model and pricing
### GPT-4o (New)
- Fastest and most affordable flagship model
- Text and image input, text output
- 128k context length
- Input: $5 | Output: $15
### GPT-4 Turbo
- High-intelligence model
- Text and image input, text output
- 128k context length
- Input: $10 | Output: $30
### GPT-3.5 Turbo _(we will most likely work with this model)_
- Fast, inexpensive model for simple tasks
- 16k context length
- More chance of "Hallucination"
- Input: $0.50 | Output: $1.50

Prices per 1 million tokens. 1 Token is approximately 4 letters or 0.75 English word.

## Chat Completions API:
**Chat Completions API** is the most basic form for us to utilize the **GPT model**.
An example API call is shown below:
```
from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Who won the world series in 2020?"},
    {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
    {"role": "user", "content": "Where was it played?"}
  ]
)
```

To query the **GPT model** we have to create a completion object. Within the completion object exists an array of message objects. 
Each message object has a role value. The first message marked with the **system** role is how we define the behavior of the **GPT model**. 
Messages marked with the **user** role are the end user’s query messages. Messages marked with the **assistant** role are replies from the **GPT model**. 
Hence this message array acts as a message log of back-and-forth conversation between the **GPT model** and the end user. 
It is important to include conversation history as the models have no memory of past requests. All related information must be 
supplied as part of the conversation history in each completion request.

An example Chat Completions API response looks as follow:
```
{
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "content": "The 2020 World Series was played in Texas at Globe Life Field in Arlington.",
        "role": "assistant"
      },
      "logprobs": null
    }
  ],
  "created": 1677664795,
  "id": "chatcmpl-7QyqpwdfhqwajicIEznoc6Q47XAyW",
  "model": "gpt-3.5-turbo-0613",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 17,
    "prompt_tokens": 57,
    "total_tokens": 74
  }
}
```

The assistant’s reply can be extracted with:
```
completion.choices[0].message.content
```

## Function Calling
Through prompts, we can assign the **GPT model** new functions, either by code or human description. For example we can 
define the **GPT model** a function to converts Celsius to Fahrenheit. Then during prompts we can tell the **GPT model** to use a specific function. 
Alternatively, if we taught the **GPT model** multiple functions, we can have it decides on it's own which function to use. 

## Other capabilities of the GPT model
GPT-4o and GPT-4 Turbo has the **Vision** capability, which enables them to receive image input. 
The model then can give a text description or answer questions about the image. Notice that in ChatGPT, if you
have paid subscription which enables the GPT-4o model, you can upload pictures to the chat. Where as if you
use the free GPT-3.5 model you cannot upload images.

## Other OpenAI otheran than the GPT model
**OpenAI** models other than the GPT model includes **DALL E** (image generation), **Vision** (image to text), **TTS** (text to speech), **Whisper** (speech to text), 
and **Embeddings** (text to numerical form). **Embeddings** is essentially useful for looking at large quantities of text as 
floating point numbers. For example we can take 10,000 reviews of an Amazon product and turn them into floating 
point numbers, call *vectors* (almost like giving each a numerical tag). The model can then use these *vectors* to search or filter through all the reviews, 
e.g. only show positive reviews. We can also cluster, or group similar reviews together, recommend similar reviews, 
detect outlier reviews, analyze how diverse the reviews are and classify similar reviews into labels. In essence, 
the **Embeddings** capability allows the GPT model and the end users to better visualize big data.

## Fine-tuning
The **GPT model** is pre-trained and is ready to use via the **Chat Completion API**. However if we are unsatisfied with the pre-trained model or want 
the model to perform in a certain way, we can further fine tune it. Fine-tuning is recommended only if using multiple 
guiding prompts does not work. Fine-tuning involve creating a training file. The file will consist of at least 10 pairs 
of example prompt and expected reply from the model, although **OpenAI** recommends 50-100 pairs. The training file must 
not exceed 1 Gb, although that much training is not needed to achieve a well-trained model. We can then create a 
fine-tuning job and upload our training file. It will take 30 minutes up to several hours to complete the training. 
We can then use the trained model and evaluate if it needs further tuning. Different versions of our trained model 
are stored as *Checkpoint Models*, which we can always revert back to if necessary. Since fine-tuning eliminates the 
need to include large quantity of pre-determined prompts every time a user interact with the **GPT model**, it can 
save costs for the users. We can tune various aspects of the model such as its style and tone, how it should structure 
it's output and define custom tools and functions that the model can use.

## Assistants API (beta)
The **Assistants API** is a newer and more advanced API than the **Chat Completions API**. It is still in its Beta. Think of the 
**Assistants API** as an easier way to fine-tune the **GPT model**. An example use of the **Assistants API** is 
AI-enhancing a large organization where its employees can utilize a centralized AI to manage the organization’s 
big data. Instead of keeping track of a message log in a completion object as in the **Chat Completions API**, the 
**Assistants API** creates a *thread* of messages, where each new message between the users and the Assistant is appended to 
the *thread*. Beyond the **GPT model**, the **Assistants API** can also access all of OpenAI models such as **DALL E**, **TTS**, 
**Whisper**, etc. Hence the organization can store all of it's documents in image form and have the **Assistants API** access 
these resources. The **Assistants API** uses the **Embeddings model** to visualize these images, which enables the employees to 
search, sort, filter or ask questions about these documents. The current limit is 100 GB per organization. Another use of the **Assistants 
API** is the **Code Interpreter**, where Assistants help software engineers with python coding. The Assistants can help fix 
bugs in python files, help format large data files, or solve code or math problems. The Assistant’s **Code Interpreter** is charged 
per hour, instead of per token.

## Notable Links
#### Guide to Prompt Engineering
https://platform.openai.com/docs/guides/prompt-engineering
#### OpenAI Cookbook (Guides / Lessons / Example implementations on various OpenAI models and APIs)
https://cookbook.openai.com
#### OpenAI Playground (For creating and testing prompts and for turning prompts into API function call code. Works for the Chat Completion API, Assistants API and Fine-tuning API)
https://platform.openai.com/playground


