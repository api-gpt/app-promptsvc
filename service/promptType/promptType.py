# CS467 Online Capstone: GPT API Challenge
# Kongkom Hiranpradit, Connor Flattum, Nathan Swaim, Noah Zajicek

from enum import Enum


# Creates an enumeration class for what type of prompt is activated
class PromptType(Enum):
    ChatCompletions = "chat"
    Embeddings = "embedded"
    Images = "image"