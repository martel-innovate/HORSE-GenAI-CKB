import pandas as pd
from pydantic import BaseModel
from typing import List

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from dotenv import load_dotenv
import os
import logging
import json

# get logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# load env variables
load_dotenv()

DB_SECRET = os.getenv('DB_SECRET')
DB_HOSTNAME = os.getenv('DB_HOSTNAME')
DB_PORT = int(os.getenv('DB_PORT'))
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')

# get model name
MODEL = os.getenv('LLM_MODEL')

class Mitigation(BaseModel):
    name: str
    priority: int

class MitigationsList(BaseModel):
    mitigations : List[Mitigation]

def check_and_process_response(mitigation_generated, attack_name):

    # convert string in dict
    json_response = json.loads(mitigation_generated)
    if isinstance(json_response, list):
        json_response = {"mitigations": json_response}

    print(f"\nattack name: {attack_name}\njson response formatted: {json_response}\n\n")

    # check response using Pydantic data models
    response_checked = MitigationsList(**json_response)

    # remove one layer
    mitigations = json_response['mitigations']

    # prepare final df with attack, mitigations, mitigations_priority
    attack_df = pd.DataFrame(mitigations)
    attack_df['attack'] = attack_name
    attack_df.columns = ['mitigation', 'mitigation_priority', 'attack']

    return attack_df

def get_session():
    # Define database connection parameters
    DATABASE_URI = f'postgresql+psycopg2://{DB_USER}:{DB_SECRET}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}'

    # Create an engine
    engine = create_engine(DATABASE_URI)

    # Create a configured "Session" class
    Session = sessionmaker(bind=engine)

    # Create a Session
    session = Session()

    return session


def insert_into_db(df_to_upload, logger):
    # get database session 
    session = get_session()

    print("Skip values already present in the database...")

    try:
        # Load each row (attack, mitigation, mitigation_priority) into table
        for _, row in df_to_upload.iterrows():
            # Use parameterized queries to prevent SQL injection
            query = text("INSERT INTO test_attack (attack, mitigation, mitigation_priority) VALUES (:attack, :mitigation, :mitigation_priority)")
            params = {
                'attack': row['attack'],
                'mitigation': row['mitigation'],
                'mitigation_priority': row['mitigation_priority']
            }

            print(params)
            
            session.execute(query, params)

        # Commit the transaction after the loop
        session.commit()
        logger.info("Data inserted successfully.")
        print("This data has been inserted successfully")

    except SQLAlchemyError as e:
        # Rollback the transaction in case of error
        print(f"PARAMS: {params}")
        session.rollback()
        logger.error(f"An error occurred: {e}")

    finally:
        # Close the session
        session.close()

    logger.info("loaded successfully!")
    return


def extract_transform_load():

    # read csv with generated responses
    file_path = f"../output/{MODEL.replace('/', '-').replace(':', '-')}_ai_generated_mitigation_responses.csv"
    generated_df = pd.read_csv(file_path)

    # for each row=attack, extract the generated mitigations and insert into the database
    for _, row in generated_df.iterrows():
    
        # process response and prepare final df
        row_to_upload = check_and_process_response(mitigation_generated=row['llama_generated'], attack_name=row['attack'])

        # insert df_to_upload into database
        insert_into_db(row_to_upload, logger)
    return

extract_transform_load()