from openai import OpenAI
from dotenv import load_dotenv
import os, re

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#generates prompt suggestions for user
def generate_suggestions(prompt):
    if prompt == None:
        default_prompt = "generate 5 coding prompts as a user asking about their own existing codebase. Be specific"
    else:
        default_prompt = prompt

    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": """
                                        You are a Prompt Generator. 
                                        You create the most relevent prompts to the data you are given
                                        Your response must be in the following format for regex processing:
         
                                        -- where is my database being used and referenced? --;
                                        -- where is encryption used in my code? --;
                                        -- the third prompt --;
                                        -- the fourth prompt --;
                                        -- the fith prompt --;
                                        you are to adhere to this pattern completely at all times.
                                        you must include --; exactly at all times
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
    