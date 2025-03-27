from scrape_attacks import search_for_attacks
from dotenv import load_dotenv
import csv
import os
import pandas as pd

# load env variables
load_dotenv()
CAPEC_URL = os.getenv('CAPEC_URL')
CAPEC_CSV_PATH = os.getenv('CAPEC_CSV_PATH')

def main():

    # write to csv
    path = CAPEC_CSV_PATH

    # main logic here
    attacks_mitigations = search_for_attacks(CAPEC_URL, n_attacks_to_search=100, only_new_attacks=True)
    print(f'attacks mit dict: {attacks_mitigations}')
    
    # Check if the file already exists and has content
    file_exists = os.path.exists(path)

    with open(path, "a", newline="") as file:
        writer = csv.writer(file)

        # Write the header only if the file does not exist or is empty
        if not file_exists or os.stat(path).st_size == 0:  # Check if the file is empty
            writer.writerow(["attacks", "mitigations"])

        for _, row in pd.DataFrame(attacks_mitigations).iterrows():
            # Write the new data
            writer.writerow([row['attacks'], row['mitigations']])


    # check if content is readable
    new_df = pd.read_csv(path)
    print(f'miti: {new_df['mitigations_list'][0][0]}')
    
        
if __name__ == "__main__":
    main()