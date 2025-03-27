import pandas as pd
import requests
import json
import time

from dotenv import load_dotenv
import os
import logging
import csv
import anthropic

# get logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# load env variables
load_dotenv()
OLLAMA_URL_GENERATE = os.getenv('OLLAMA_URL_GENERATE')
MODEL = os.getenv('LLM_MODEL')

def prepare_request_json(attacks_mitigations_row):
    attack = attacks_mitigations_row['attacks']
    mitigation_list = attacks_mitigations_row['mitigations']

    prompt = f"return a list of mitigation names and their priority, in json format, for the attack '{attack}', including and expanding this mitigation list according to CAPEC {mitigation_list}. Please generate data in the following JSON format: The root object contains a key named 'mitigations', 'mitigations' should be an array of objects and each object in the 'mitigations' array should have two fields: 'name'(A string that provides the name of the mitigation), 'priority'(An integer that indicates the priority of the mitigation, with 1 being the highest priority). Priorities are ordered unique numbers, where 1 means that the mitigation is urgent and will be applied first, then all the others will be applied in order and there can't be two mitigations with the same priority. In the response I just want the json with no other text"

    # Data to be sent in the POST request
    if MODEL == 'claude-3-5-sonnet-20241022':
        data = {"role": "user", "content": prompt}
    else:
        data = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }

    print(f'prompt: {prompt}')
    return data

def write_to_csv(file_path, attack, mitigation_list, llm_response):
    with open(file_path, mode='a+', newline='') as file:
        writer = csv.writer(file)

        # Write the attack, mitigation, generated content and metrics to the CSV
        writer.writerow([attack, mitigation_list, llm_response['response'], llm_response['model'], llm_response['created_at'], llm_response['total_duration'], llm_response['load_duration'], llm_response['prompt_eval_count'], llm_response['prompt_eval_duration'], llm_response['eval_count'], llm_response['eval_duration']])

    print("Data saved to csv successfully.")
    return

def write_header_csv(file_path):
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Write the header if the file is empty
            writer.writerow(['attack', 'mitigation_list', 'mitigations_generated', 'model', 'created_at', 'total_duration', 'load_duration', 'prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_duration'])

def generate_mitigations(attacks_mitigations_df):
    file_path = f"../output/{MODEL.replace('/', '-').replace(':', '-')}_ai_generated_mitigation_responses.csv"
    write_header_csv(file_path)
    output_df = pd.read_csv(file_path)

    # iterate over attacks and at each step generate the mitigation list and their priority using an LLM
    for _, row in attacks_mitigations_df.iterrows():
        attack_name = row['attacks']

        # print attack name
        print(f"Generating mitigations for attack named '{attack_name}'")

        # check if attack is already in output file
        if attack_name in output_df['attack'].values:
            print(f"Attack '{attack_name}' is already in the file. Skip this attack.")
            continue
        if MODEL == 'claude-3-5-sonnet-20241022':   #use Anthropic API to send request
             # create data to send
            data = prepare_request_json(row)

            # Make the request and retrieve the generated mitigations and mitigations priority
            client = anthropic.Anthropic()
            start_time = time.time()
            message = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[
                data
            ]
            )
            end_time = time.time()
            total_duration = int((end_time - start_time) * 1e9)

            llm_response = {'response' : message.content[0].text, 'model' : MODEL, 'created_at' : start_time, 'total_duration' : total_duration, 'load_duration' : '', 'prompt_eval_count' : '', 'prompt_eval_duration' : '', 'eval_count' : '', 'eval_duration' : ''}

            # save response content in a csv
            write_to_csv(file_path, row['attacks'], row['mitigations'], llm_response)

        else:

            # create data to send
            data = prepare_request_json(row)

            # Make the POST request and retrieve the generated mitigations and mitigations priority
            response = requests.post(url=OLLAMA_URL_GENERATE, headers={'Content-Type': 'application/json'}, data=json.dumps(data))

            # save response content in a csv
            write_to_csv(file_path, row['attacks'], row['mitigations'], response.json())

    logger.info("The upload of all attacks was successful.")

    return

