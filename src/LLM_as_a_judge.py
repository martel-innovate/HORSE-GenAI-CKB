import anthropic
import pandas as pd
from dotenv import load_dotenv
import os
import csv
import requests
import json

# load env variables
load_dotenv()
LLM_MODEL = os.getenv('LLM_MODEL')
LLM_JUDGE = os.getenv('LLM_JUDGE')
JUDGE_PATH = os.getenv('JUDGE_PATH')
OLLAMA_URL_GENERATE = os.getenv('OLLAMA_URL_GENERATE')

def read_exctract_csv():
    filepath = f"../output/{LLM_MODEL.replace('/', '-').replace(':', '-')}_ai_generated_mitigation_responses.csv"
    df_ai_generated = pd.read_csv(filepath)
    return df_ai_generated

def prepare_request_json(attacks_mitigations_row):
    attack = attacks_mitigations_row['attack']
    mitigations_list = attacks_mitigations_row['mitigation_list']

    initial_prompt = f"return a list of mitigation names and their priority, in json format, for the attack '{attack}', including and expanding this mitigation list according to CAPEC {mitigations_list}. Please generate data in the following JSON format: The root object contains a key named 'mitigations', 'mitigations' should be an array of objects and each object in the 'mitigations' array should have two fields: 'name'(A string that provides the name of the mitigation), 'priority'(An integer that indicates the priority of the mitigation, with 1 being the highest priority). Priorities are ordered unique numbers, where 1 means that the mitigation is urgent and will be applied first, then all the others will be applied in order and there can't be two mitigations with the same priority. In the response I just want the json with no other text"

    response = attacks_mitigations_row['mitigations_generated']

    prompt = f"You are an expert in cybersecurity. Please act as an impartial judge and evaluate the quality of the response provided by an AI assistant to the user question displayed below. Your evaluation should consider factors such as format and correctness of the content. Begin your evaluation by providing a short explanation. Be as objective as possible. After providing your explanation, please rate the response on a scale of 1 to 5 by strictly following this format: '[[rating]]', for example: 'Rating: [[5]]'. User question: {initial_prompt}. AI assistant response: {response}"


    # Data to be sent in the POST request
    if LLM_JUDGE == 'claude-3-5-sonnet-20241022':
        data = {"role": "user", "content": prompt}
    else:
        data = {
            "model": LLM_JUDGE,
            "prompt": prompt,
            "stream": False
        }

    print(f'prompt: {data}')
    return data


def write_to_csv(file_path, row, evaluation, llm_judge):
    with open(file_path, mode='a+', newline='') as file:
        writer = csv.writer(file)

        # Write the attack, mitigation, generated content and metrics to the CSV
        writer.writerow([row['attack'], row['mitigation_list'], row['mitigations_generated'], row['model'], llm_judge, evaluation])

    print("Data saved to csv successfully.")
    return


def write_header_csv(file_path):
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Write the header if the file is empty
            writer.writerow(['attack', 'mitigation_list', 'mitigations_generated', 'model', 'llm_judge', 'evaluation_generated'])


def generate_evaluations(df_ai_generated):
    file_path = f"../evaluation/LLMs/{JUDGE_PATH}/{LLM_MODEL.replace('/', '-').replace(':', '-')}_ai_generated_evaluations.csv"
    write_header_csv(file_path)
    output_df = pd.read_csv(file_path)

    # iterate over attacks and at each step generate the mitigation list and their priority using an LLM
    for _, row in df_ai_generated.iterrows():
        attack = row['attack']

        # print attack name
        print(f"Generating evaluation for attack named '{attack}'")

        # check if attack is already in output file
        if attack in output_df['attack'].values:
            print(f"Attack '{attack}' is already in the file. Skip this attack.")
            continue
        if LLM_JUDGE == 'claude-3-5-sonnet-20241022':   #use Anthropic API to send request
            # create data to send
            data = prepare_request_json(row)

            # make request
            client = anthropic.Anthropic()
            message = client.messages.create(
            model=LLM_JUDGE,
            max_tokens=1024,
            messages=[
                data
            ]
            )
            write_to_csv(file_path, row, message.content, message.model)
        
        else:   # use OLLAMA API to send request

            # create data to send
            data = prepare_request_json(row)

            # make the POST request and retrieve the generated mitigations and mitigations priority
            response = requests.post(url=OLLAMA_URL_GENERATE, headers={'Content-Type': 'application/json'}, data=json.dumps(data))

            # save response content in a csv
            response = response.json()
            write_to_csv(file_path, row, response["response"], response["model"])
    return


def main():
    df_ai_generated = read_exctract_csv()
    generate_evaluations(df_ai_generated)

if __name__ == "__main__":
    main()