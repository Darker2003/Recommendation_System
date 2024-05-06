import json
import os
import re

import pandas as pd
import torch
from transformers import AutoModel, AutoTokenizer

#prompt convert
DEFAULT_TEXT_ANNOTATION_FILE = "Datasets/Query/datasets_text.json"

#Set the GPT API Key
# os.environ["OPENAI_API_KEY"] = 
gpt_model_name = "gpt-3.5-turbo"
prompt_path = "Datasets/Prompt/prompt.json"

#Question
question = {"role": "user", "content": "Tôi muốn đi cắm trại ngắm bình minh cùng gia đình trên biển"}

#Calculate similarity
MAX_LENGTH = 200
places_data_path = "Datasets/Places/destination_1.xlsx"
top_n = 5 #top n highest score suggestion
phobert_model_name = "vinai/phobert-base-v2"


def load_json_file(file_path):
    print(f"Loading  JSON file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def GPT_prompt(prompt_path):
    #Get the prompt form
    # Assuming the JSON data is stored in a file named 'data.json'
    with open(prompt_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    # Now, json_data contains the parsed JSON data as a Python dictionary
    # You can access its elements like you would with any Python dictionary
    return json_data

# Clear and Get tags of place
# def get_place_tags(places_data_path):
#     place_tags = pd.read_excel(places_data_path)
#     place_tags = list(place_tags['tags'])
#     place_tags = [re.sub(r',', '', string) for string in place_tags]
#     return  place_tags