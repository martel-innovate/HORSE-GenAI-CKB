from dotenv import load_dotenv
from mitigation_generator import generate_mitigations

import csv
import os
import pandas as pd

# load env variables
load_dotenv()
CSV_PATH = os.getenv('CAPEC_CSV_PATH')
N = int(os.getenv('N_ATTACKS'))

def main():
    attacks_mitigations_df = pd.read_csv(CSV_PATH)
    attacks_mitigations_df = attacks_mitigations_df[:N]

    # enhance the database with generative AI
    generate_mitigations(attacks_mitigations_df)

if __name__ == "__main__":
    main()