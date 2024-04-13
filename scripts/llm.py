import time
import os
import pandas as pd
from openai import OpenAI

from helper import build_prompt


def append_llm_output(df: pd.DataFrame, payload: dict, result_col: str) -> pd.DataFrame:
    """
    Updates the original DataFrame by assigning generated topic labels to each snippet
    based on the index of the snippet.
    :param df: pd.DataFrame, dataframe with snippets that need topic labels.
    :param payload: dict, prompt payload
    :return: pd.DataFrame, validation set plus updated 'gpt_topic_label' column
    """
    for index, row in df.iterrows():
        payload["snippet"] = row['snippet']

        # Generate the output for the snippet
        output = generate_llm_output(payload)
        
        # Update the DataFrame directly at the current index
        df.at[index, result_col] = output

        # Buffer between calls
        time.sleep(3)
        
    return df


def generate_llm_output(payload: dict=None) -> str:
    """
    Generates response from LLM.
    :param payload: dict, prompt and snippet payload
    :return: str, snippet topic label
    """
    start_time = time.time()
    try:
        snippet = payload["snippet"]
        if not snippet:
            return "No news snippet to analyze."
        else:
            # Create LLM prompt
            sys_prompt, intro, instruct = payload['system_prompt'], payload['introduction'], payload['instruction']
            prompt = build_prompt(sys_prompt, intro, instruct, snippet)

            model_urls = [
                "gpt-3.5-turbo-0125", 
                "gpt-4",
                "text-embedding-3-small"
                ]
            response = get_llm_response(prompt, model_urls[0])
            if response == "Unknown":
                time.sleep(2) 
                response = get_llm_response(prompt, model_urls[0]) 

            return response
        
    except Exception as e:
        print(f"An error {e} occurred when generating response.")
        
    print(f"Elapsed runtime: {round(time.time() - start_time, 2)} seconds.")


def get_llm_response(prompt: str, model_url: str) -> str:
    """
    Get response from ChatGPT.
    :param prompt: str, instruction prompt for LLM
    :param model_url: str, model name
    :return: str, LLM response
    """
    
    if model_url in ["gpt-3.5-turbo-0125", "gpt-4"]:
        client = OpenAI(api_key=os.environ.get('OPEN_AI_KEY'))

        response = client.chat.completions.create(
            model = model_url,
            messages = [{"role": "user", "content": prompt}],
            temperature = 0.7,
        )
        return response.choices[0].message.content 