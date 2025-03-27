from urllib.request import urlopen
from scrape_mitigations import scrape_from_attack_page
import re
import pandas as pd
import os
from dotenv import load_dotenv

# load env variables
load_dotenv()

CAPEC_CSV_PATH = os.getenv('CAPEC_CSV_PATH')

def search_attack_page_url(string):
    # search in the string the url of the attack. Note that url of attacks always start with /data/definition
    pattern = re.compile(r'href="(/data/definitions/.[^"]+)"')
    match = pattern.search(string)

    if match:
        endpoint =  match.group(1).strip()
        # create complete url of the attack page
        url = f"https://capec.mitre.org{endpoint}"
    else:
        print(f"No matching url found in string {string}.")
        url = None
    return url

def read_page(url):
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    return html

def extract_attack_matches(page_content):
    """Extract potential attack matches from the page content."""
    pattern = re.compile(r'alt=\"Detailed Attack Pattern\"(.*?)<span class="capecid Primary">')
    return pattern.findall(page_content)

def extract_attack_name(string_with_attack_name):
    """Extract the attack name from the string."""
    pattern = re.compile(r'rel="noopener noreferrer">([a-zA-Z :\'"\/\\,()-]+)')
    match = pattern.search(string_with_attack_name)
    return match.group(1).strip() if match else None

def process_attack(string_with_attack_name, attack_dict, output_df, only_new_attacks):
    """Process a single attack, extracting the name and URL, and add it to the dictionary."""
    attack_name = extract_attack_name(string_with_attack_name)

    if attack_name:     
        if only_new_attacks and attack_name in output_df['attack'].values:
            # attack already in output file
            print(f"Attack '{attack_name}' is already in the file. Skip this attack.")
        else:
            print(f"Attack named {attack_name} not found in the file. It will be added.")
            attack_dict["attack_name"].append(attack_name)

            # Search for url of the attack page
            attack_dict["attack_page_url"].append(search_attack_page_url(string_with_attack_name))
    else:
        print("No attack name found")
    return attack_dict

def scrape_attack_name(url, n_attacks_to_search, only_new_attacks):
    attack_dict = {"attack_name" : [], "attack_page_url" : []}

    # Define the path to the CSV file
    csv_path = CAPEC_CSV_PATH

    # Check if the file exists and is not empty
    if os.path.exists(csv_path):
        try: 
            output_df = pd.read_csv(csv_path)
            if output_df.empty:
                output_df = pd.DataFrame(columns=['attack'])  # Create DataFrame with 'attack' column if the file is empty
        except pd.errors.EmptyDataError:
            # File is empty, create an empty DataFrame with 'attack' column
            output_df = pd.DataFrame(columns=['attack'])
    else:
        # File does not exist, create an empty DataFrame with 'attack' column
        output_df = pd.DataFrame(columns=['attack'])

    # Read main page
    page_content = read_page(url)

    # Search for match = attacks
    matches = extract_attack_matches(page_content)

    if matches:

        for match in matches:
            attack_dict = process_attack(match, attack_dict, output_df, only_new_attacks)
            # Stop when the correct number of attacks has been found
            if len(attack_dict["attack_name"]) >= n_attacks_to_search:
                break
    else:
        print("No matching content found.")
    return attack_dict

def scrape_mitigation_name(url_attack):
    if url_attack is not None:
        # Found a url of the attack. Scrape that page to search for mitigations
        mitigation_list = scrape_from_attack_page(url_attack)   # can return empty list
        return mitigation_list
    else:
        print("No url found for this attack")
        return []

def search_for_attacks(url, n_attacks_to_search, only_new_attacks):
    """ Searches for attack names and their corresponding mitigations from a given url """
    attack_mitigation_dict = {"attacks" : [], "mitigations" : []}

    # search attacks and attack url
    print("Searching for attack names...")
    attack_dict = scrape_attack_name(url, n_attacks_to_search, only_new_attacks)
    attack_mitigation_dict["attacks"] = attack_dict["attack_name"]
    print(f"Found {len(attack_mitigation_dict['attacks'])} attacks.\n")

    print("Searching for mitigations...")

    for attack_url in attack_dict["attack_page_url"]:
        # for each attack, scrape mitigation list
        attack_mitigation_dict["mitigations"].append(scrape_mitigation_name(attack_url))

    print(f"Final attack_mitigation_dict: \n{attack_mitigation_dict}")
    return attack_mitigation_dict
