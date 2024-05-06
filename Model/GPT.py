import json

from openai import OpenAI

from .config import *

client = OpenAI()

def GPT(question):
    message = GPT_prompt(prompt_path)
    message.append(question)

    response = client.chat.completions.create(
        model=gpt_model_name,
        response_format={"type": "json_object"},
        messages=message,
        temperature = 0
    )
    tags = []
    for tag in json.loads(response.choices[0].message.content)['entities']:
        tag[1] = tag[1].replace(" ", "_")
        tags.append(tag[1])
    print(tags)
    return [" ".join(tags)]

if __name__ ==  '__main__':
    GPT(question)