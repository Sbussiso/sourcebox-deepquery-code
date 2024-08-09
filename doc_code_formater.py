from openai import OpenAI
from dotenv import load_dotenv
import os, re

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_suggestions(prompt):
    if prompt == None:
        default_prompt = "Format this code:"
    else:
        default_prompt = prompt

    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": """
                                        You are a code formating tool. 
                                        You are to take strings
                                        ....."""},

        {"role": "user", "content": str(default_prompt)},
    ]
    )
    message = response.choices[0].message.content
    print(message)

    # Define the regex pattern
    pattern = r'--\s(.*?)\s--;'
    # Find all matches
    matches = re.findall(pattern, message)
    print("matches found:\n\n\n")

    # Print the results
    return matches


if __name__ == "__main__":
    prompt = None
    generate_suggestions(prompt)
    